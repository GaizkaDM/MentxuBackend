# ==============================================================================
# 📊 MÓDULO DE ESTADÍSTICAS - DIdaktikAPP / MentxuApp
# ==============================================================================
# 
# Este módulo implementa un sistema completo de estadísticas educativas
# con las siguientes características:
#
# 🎯 NIVEL AVANZADO (10/10):
#   - POO Compleja: herencia, polimorfismo, encapsulación
#   - Exportación múltiple: CSV, JSON, Excel con filtros
#   - ORM SQLAlchemy con relaciones complejas
#   - API REST completa con Flask
#   - Dashboard interactivo con gráficos
#
# 📦 ESTRUCTURA:
#   estadisticas/
#   ├── __init__.py           # Este archivo - Blueprint principal
#   ├── models/               # Modelos ORM (SQLAlchemy)
#   │   ├── __init__.py
#   │   ├── base.py           # Clases base abstractas
#   │   ├── sesion.py         # Modelo de sesiones (login)
#   │   ├── logro.py          # Sistema de logros
#   │   └── historial.py      # Histórico de intentos
#   ├── services/             # Lógica de negocio (POO)
#   │   ├── __init__.py
#   │   ├── base_service.py   # Servicio base abstracto
#   │   ├── estadisticas_service.py
#   │   └── logros_service.py
#   ├── exporters/            # Exportación de datos
#   │   ├── __init__.py
#   │   ├── base_exporter.py  # Exportador base (Factory Pattern)
#   │   ├── csv_exporter.py
#   │   ├── json_exporter.py
#   │   └── excel_exporter.py
#   ├── routes/               # API REST endpoints
#   │   ├── __init__.py
#   │   ├── estadisticas_api.py
#   │   ├── logros_api.py
#   │   └── exportar_api.py
#   └── templates/            # Templates HTML (Dashboard)
#       ├── estadisticas_base.html
#       ├── estadisticas_dashboard.html
#       ├── estadisticas_usuarios.html
#       └── estadisticas_actividades.html
#
# ==============================================================================

from flask import Blueprint

# Blueprint principal del módulo de estadísticas
estadisticas_bp = Blueprint(
    'estadisticas', 
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/estadisticas'
)

# Importar y registrar sub-blueprints
def init_estadisticas(app, db):
    """
    Inicializa el módulo de estadísticas.
    Debe llamarse después de crear la app Flask.
    
    Args:
        app: Instancia de Flask
        db: Instancia de SQLAlchemy
    """
    from .routes import estadisticas_api_bp, logros_api_bp, exportar_api_bp
    
    # Registrar blueprints de API
    estadisticas_bp.register_blueprint(estadisticas_api_bp)
    estadisticas_bp.register_blueprint(logros_api_bp)
    estadisticas_bp.register_blueprint(exportar_api_bp)
    
    # Registrar el blueprint principal en la app
    app.register_blueprint(estadisticas_bp)
    
    # Crear tablas si no existen
    with app.app_context():
        from .models import Sesion, Logro, LogroUsuario, HistorialIntento
        db.create_all()
        print("✅ Módulo de estadísticas inicializado")
    
    return estadisticas_bp


# Información del módulo
__version__ = "1.0.0"
__author__ = "DIdaktikAPP Team"
__description__ = "Sistema avanzado de estadísticas educativas"
