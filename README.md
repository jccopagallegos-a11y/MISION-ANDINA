# MISIÓN ANDINA 🚀
**Simulador educativo de diseño y planificación de misiones espaciales**  
Estudiante: Juan CCOPA GALLEGOS  
Curso: Desarrollo de Aplicaciones Web con Python Flask y SQLite

## Descripción
Proyecto académico inspirado en el desafío **Space Mission Design Game** de NASA Space Apps Challenge 2026. Permite registrar usuarios, diseñar misiones, administrar parámetros básicos y ejecutar una evaluación educativa que muestra cómo presupuesto, masa, potencia y comunicaciones afectan el resultado.

> La simulación utiliza umbrales didácticos simplificados. No representa predicciones orbitales ni cálculos certificados de ingeniería aeroespacial.

## Funcionalidades
- Registro, login y logout con contraseñas cifradas.
- Roles `user` y `admin`; el administrador consulta el listado de usuarios.
- CRUD de misiones por propietario.
- Simulación y puntuación de misión.
- Reportes e historial.
- Pruebas automatizadas con pytest.

## Requisitos
Python 3.10 o superior.

## Instalación local
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Abrir http://127.0.0.1:5000

La base de datos se crea automáticamente en `instance/mision_andina.sqlite`.

## Crear un administrador
Por seguridad no existe una contraseña administrativa predeterminada. Registra una cuenta desde la web y luego ejecuta:
```bash
python make_admin.py correo@ejemplo.com
```

## Pruebas
```bash
pytest -v
```

## Publicar en GitHub
1. Crea un repositorio público llamado `mision-andina`.
2. En esta carpeta ejecuta:
```bash
git init
git add .
git commit -m "Primera versión de Misión Andina"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/mision-andina.git
git push -u origin main
```

## Desplegar en Render
1. Sube el repositorio a GitHub.
2. En Render elige **New > Blueprint** y conecta el repositorio.
3. Render leerá `render.yaml`; revisa que se cree el disco persistente.
4. Espera el despliegue y abre la URL asignada.
5. Conserva la URL para incluirla en el informe.

## Evidencias para el PDF
Captura: portada, registro, login, dashboard, crear misión, listado, edición, eliminación, resultado de simulación, reportes, usuarios admin, `pytest -v` y aplicación publicada.

## Desafío y contexto
NASA Space Apps Challenge 2026, **Space Mission Design Game**: crear un juego interactivo que permita diseñar, gestionar y simular una misión completa tomando decisiones de ingeniería con recursos limitados.
Enlace: https://www.spaceappschallenge.org/2026/challenges/space-mission-design-game/

La inscripción y el envío oficial a NASA Space Apps deben completarse en la plataforma del evento por el participante. Este repositorio no constituye por sí mismo un certificado de participación.
