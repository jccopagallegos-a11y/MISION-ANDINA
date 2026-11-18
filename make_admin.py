import sys, os, sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash
if len(sys.argv) != 2:
    print("Uso: python make_admin.py correo@ejemplo.com"); raise SystemExit(1)
db_path = os.environ.get("DATABASE_PATH", str(Path("instance") / "mision_andina.sqlite"))
con = sqlite3.connect(db_path)
cur = con.execute("UPDATE users SET role='admin' WHERE email=?", (sys.argv[1].lower(),))
con.commit()
print("Rol administrador actualizado." if cur.rowcount else "No se encontró ese correo.")
con.close()
