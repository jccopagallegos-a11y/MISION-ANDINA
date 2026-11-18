import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_db, init_db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion"),
        DATABASE=os.environ.get("DATABASE_PATH", os.path.join(app.instance_path, "mision_andina.sqlite")),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def close_db(exception=None):
        db = getattr(__import__("flask").g, "_database", None)
        if db is not None:
            db.close()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Inicia sesión para continuar.", "warning")
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    def admin_required(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            db = get_db()
            user = db.execute("SELECT role FROM users WHERE id=?", (session["user_id"],)).fetchone()
            if not user or user["role"] != "admin":
                abort(403)
            return view(*args, **kwargs)
        return wrapped

    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("index.html")

    @app.route("/registro", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not name or not email or len(password) < 6:
                flash("Completa todos los campos. La contraseña debe tener al menos 6 caracteres.", "danger")
                return render_template("register.html")
            db = get_db()
            try:
                db.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                           (name, email, generate_password_hash(password), "user", datetime.utcnow().isoformat()))
                db.commit()
            except Exception:
                flash("Ese correo ya está registrado.", "danger")
                return render_template("register.html")
            flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                flash("Bienvenido a la estación de control.", "success")
                return redirect(url_for("dashboard"))
            flash("Correo o contraseña incorrectos.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Sesión cerrada correctamente.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        missions = db.execute("SELECT * FROM missions WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
                              (session["user_id"],)).fetchall()
        stats = db.execute("""SELECT COUNT(*) total,
            SUM(CASE WHEN status='Exitosa' THEN 1 ELSE 0 END) successful,
            COALESCE(SUM(budget),0) budget FROM missions WHERE user_id=?""",
                           (session["user_id"],)).fetchone()
        return render_template("dashboard.html", missions=missions, stats=stats)

    @app.route("/misiones")
    @login_required
    def missions():
        rows = get_db().execute("SELECT * FROM missions WHERE user_id=? ORDER BY created_at DESC",
                                (session["user_id"],)).fetchall()
        return render_template("missions.html", missions=rows)

    @app.route("/misiones/nueva", methods=["GET", "POST"])
    @login_required
    def new_mission():
        if request.method == "POST":
            data = mission_form_data()
            error = validate_mission(data)
            if error:
                flash(error, "danger")
                return render_template("mission_form.html", mission=data, heading="Nueva misión")
            db = get_db()
            db.execute("""INSERT INTO missions
                (user_id,name,objective,destination,spacecraft,launcher,instruments,budget,mass,power,communications,status,score,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (session["user_id"], data["name"], data["objective"], data["destination"], data["spacecraft"],
                 data["launcher"], data["instruments"], data["budget"], data["mass"], data["power"],
                 data["communications"], "En diseño", 0, datetime.utcnow().isoformat()))
            db.commit()
            flash("Misión registrada correctamente.", "success")
            return redirect(url_for("missions"))
        return render_template("mission_form.html", mission={}, heading="Nueva misión")

    @app.route("/misiones/<int:mission_id>/editar", methods=["GET", "POST"])
    @login_required
    def edit_mission(mission_id):
        db = get_db()
        mission = db.execute("SELECT * FROM missions WHERE id=? AND user_id=?",
                             (mission_id, session["user_id"])).fetchone()
        if not mission:
            abort(404)
        if request.method == "POST":
            data = mission_form_data()
            error = validate_mission(data)
            if error:
                flash(error, "danger")
                return render_template("mission_form.html", mission=data, heading="Editar misión")
            db.execute("""UPDATE missions SET name=?,objective=?,destination=?,spacecraft=?,launcher=?,instruments=?,
                budget=?,mass=?,power=?,communications=? WHERE id=? AND user_id=?""",
                (data["name"], data["objective"], data["destination"], data["spacecraft"], data["launcher"],
                 data["instruments"], data["budget"], data["mass"], data["power"], data["communications"],
                 mission_id, session["user_id"]))
            db.commit()
            flash("Misión actualizada.", "success")
            return redirect(url_for("missions"))
        return render_template("mission_form.html", mission=mission, heading="Editar misión")

    @app.route("/misiones/<int:mission_id>/eliminar", methods=["POST"])
    @login_required
    def delete_mission(mission_id):
        db = get_db()
        db.execute("DELETE FROM missions WHERE id=? AND user_id=?", (mission_id, session["user_id"]))
        db.commit()
        flash("Misión eliminada.", "info")
        return redirect(url_for("missions"))

    @app.route("/misiones/<int:mission_id>/simular", methods=["POST"])
    @login_required
    def simulate(mission_id):
        db = get_db()
        mission = db.execute("SELECT * FROM missions WHERE id=? AND user_id=?",
                             (mission_id, session["user_id"])).fetchone()
        if not mission:
            abort(404)
        score, status, notes = evaluate_mission(mission)
        db.execute("UPDATE missions SET score=?, status=? WHERE id=? AND user_id=?",
                   (score, status, mission_id, session["user_id"]))
        db.commit()
        return render_template("simulation.html", mission=mission, score=score, status=status, notes=notes)

    @app.route("/reportes")
    @login_required
    def reports():
        rows = get_db().execute("SELECT * FROM missions WHERE user_id=? ORDER BY created_at DESC",
                                (session["user_id"],)).fetchall()
        return render_template("reports.html", missions=rows)

    @app.route("/admin/usuarios")
    @admin_required
    def admin_users():
        users = get_db().execute("SELECT id,name,email,role,created_at FROM users ORDER BY id").fetchall()
        return render_template("admin_users.html", users=users)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("error.html", code=403, message="No tienes permisos para acceder a esta sección."), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="No encontramos el recurso solicitado."), 404

    def mission_form_data():
        f = request.form
        def number(key):
            try: return float(f.get(key, "0"))
            except ValueError: return -1
        return {
            "name": f.get("name", "").strip(), "objective": f.get("objective", "").strip(),
            "destination": f.get("destination", "Marte"), "spacecraft": f.get("spacecraft", "").strip(),
            "launcher": f.get("launcher", "").strip(), "instruments": f.get("instruments", "").strip(),
            "budget": number("budget"), "mass": number("mass"), "power": number("power"),
            "communications": f.get("communications", "Básica")
        }

    def validate_mission(d):
        if not d["name"] or not d["objective"] or not d["spacecraft"] or not d["launcher"]:
            return "Completa nombre, objetivo, nave y cohete."
        if any(d[k] < 0 for k in ("budget", "mass", "power")):
            return "Los recursos deben ser números iguales o mayores que cero."
        return None

    def evaluate_mission(m):
        notes = []
        score = 100
        # Umbrales didácticos y explícitos, no parámetros de ingeniería reales.
        if m["budget"] < 100: score -= 25; notes.append("Presupuesto limitado: menos de 100 millones.")
        else: notes.append("Presupuesto dentro del umbral didáctico.")
        if m["mass"] > 1200: score -= 25; notes.append("La masa supera 1,200 kg; revisa la capacidad de lanzamiento.")
        else: notes.append("Masa dentro del límite didáctico.")
        if m["power"] < 500: score -= 20; notes.append("Potencia insuficiente para el perfil de misión propuesto.")
        else: notes.append("Potencia disponible suficiente según el modelo.")
        if m["communications"] == "Básica": score -= 10; notes.append("Comunicaciones básicas: mayor riesgo de pérdida de datos.")
        else: notes.append("Sistema de comunicaciones avanzado seleccionado.")
        score = max(0, min(100, score))
        status = "Exitosa" if score >= 75 else ("En riesgo" if score >= 50 else "No viable")
        return score, status, notes

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
