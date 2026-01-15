from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def init_database(app):
    """Inicializa la base de datos si no existe"""
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Detectar si es SQLite o PostgreSQL
        is_sqlite = db_uri.startswith('sqlite:///')
        is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
        
        should_init = False
        
        if is_sqlite:
            # Para SQLite, verificar si el archivo existe
            db_path = db_uri.replace('sqlite:///', '')
            should_init = not os.path.exists(db_path)
        elif is_postgres:
            # Para PostgreSQL, verificar si las tablas existen
            from app.models import Admin
            try:
                Admin.query.first()
                print("✅ Base de datos PostgreSQL ya tiene tablas")
            except:
                should_init = True
                print("🔄 PostgreSQL detectado, inicializando tablas...")
        
        if should_init:
            print("🔄 Base de datos no encontrada o tablas faltantes. Creándola...")
            try:
                # Crear todas las tablas
                db.create_all()
                print("✅ Tablas creadas")
            except Exception as e:
                print(f"❌ Error al crear tablas: {e}")
        
        # SIEMPRE verificar Admin y Paradas (fuera del check inicial de tablas)
        with app.app_context():
            try:
                from app.models import Admin, Parada
                
                # Sincronizar Admin
                admin_username = os.getenv('ADMIN_USERNAME', 'admin')
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                
                admin = Admin.query.filter_by(username=admin_username).first()
                if not admin:
                    admin = Admin(username=admin_username)
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    print(f"✅ Admin creado: {admin_username}")
                else:
                    # Opcional: actualizar password si cambia en variables de entorno
                    admin.set_password(admin_password)
                    print(f"✅ Admin verificado/actualizado: {admin_username}")
                
                # Sincronizar Paradas (Coordenadas correctas de Santurtzi)
                if Parada.query.count() == 0:
                    paradas_data = [
                        {'nombre': 'Santurtziko Udala (Mentxu)', 'latitud': 43.328833, 'longitud': -3.032944, 'tipo_juego': 'Sopa de Letras', 'orden': 1},
                        {'nombre': '"El niño y el perro" eskultura', 'latitud': 43.328833, 'longitud': -3.032306, 'tipo_juego': 'Diferencias', 'orden': 2},
                        {'nombre': 'Agurtza itsasontzia', 'latitud': 43.327000, 'longitud': -3.023778, 'tipo_juego': 'Relacionar', 'orden': 3},
                        {'nombre': 'Itsas-museoa', 'latitud': 43.330639, 'longitud': -3.030750, 'tipo_juego': 'Basura', 'orden': 4},
                        {'nombre': 'Itsas-portua', 'latitud': 43.330417, 'longitud': -3.030722, 'tipo_juego': 'Pesca', 'orden': 5},
                        {'nombre': '"Monumento niños y niñas de la guerra" eskultura', 'latitud': 43.330500, 'longitud': -3.029917, 'tipo_juego': 'Puzzle', 'orden': 6}
                    ]
                    
                    for p_data in paradas_data:
                        nueva_parada = Parada(
                            nombre=p_data['nombre'],
                            nombre_corto=p_data['nombre'],
                            latitud=p_data['latitud'],
                            longitud=p_data['longitud'],
                            descripcion=f"Parada {p_data['orden']}",
                            tipo_juego=p_data['tipo_juego'],
                            orden=p_data['orden']
                        )
                        db.session.add(nueva_parada)
                    print(f"✅ {len(paradas_data)} paradas creadas con coordenadas correctas")
                
                db.session.commit()
            except Exception as e:
                print(f"❌ Error al sincronizar datos iniciales: {e}")
                db.session.rollback()

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Crear carpeta instance si no existe
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"✅ Carpeta instance creada")
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    # Inicializar base de datos automáticamente
    init_database(app)
    
    # Registrar blueprints
    from app.routes.web import web_bp
    from app.routes.auth import auth_bp
    from app.routes.paradas import paradas_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.progreso import progreso_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(paradas_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(progreso_bp, url_prefix='/api')
    
    return app
