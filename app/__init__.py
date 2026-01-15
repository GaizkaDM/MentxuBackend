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
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print("🔄 Base de datos no encontrada. Creándola...")
            
            try:
                from app.models import Admin, Parada
                
                # Crear todas las tablas
                db.create_all()
                print("✅ Tablas creadas")
                
                # Crear admin por defecto
                admin_username = os.getenv('ADMIN_USERNAME', 'admin')
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                
                if not Admin.query.filter_by(username=admin_username).first():
                    admin = Admin(username=admin_username)
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    print(f"✅ Admin creado: {admin_username}")
                
                # Crear paradas de Santurtzi
                if Parada.query.count() == 0:
                    paradas = [
                        Parada(nombre='Ayuntamiento de Santurtzi (Mentxu)', nombre_corto='Ayuntamiento',
                               latitud=43.3289, longitud=-3.0323, descripcion='Punto de inicio',
                               tipo_juego='Sopa de Letras', orden=1),
                        Parada(nombre='Escultura "El niño y el perro"', nombre_corto='Escultura',
                               latitud=43.3275, longitud=-3.0310, descripcion='Famosa escultura',
                               tipo_juego='Diferencias', orden=2),
                        Parada(nombre='Barco Agurtza', nombre_corto='Barco',
                               latitud=43.3265, longitud=-3.0295, descripcion='Histórico barco',
                               tipo_juego='Relacionar', orden=3),
                        Parada(nombre='Museo Marítimo', nombre_corto='Museo',
                               latitud=43.3258, longitud=-3.0288, descripcion='Museo marítimo',
                               tipo_juego='Basura', orden=4),
                        Parada(nombre='Puerto Pesquero', nombre_corto='Puerto',
                               latitud=43.3270, longitud=-3.0305, descripcion='Puerto pesquero',
                               tipo_juego='Pesca', orden=5),
                        Parada(nombre='Monumento', nombre_corto='Monumento',
                               latitud=43.3280, longitud=-3.0315, descripcion='Conmemoración',
                               tipo_juego='Puzzle', orden=6)
                    ]
                    for p in paradas:
                        db.session.add(p)
                    print(f"✅ {len(paradas)} paradas creadas")
                
                db.session.commit()
                print("✅ Base de datos inicializada correctamente")
            except Exception as e:
                print(f"❌ Error al inicializar BD: {e}")
                db.session.rollback()
        else:
            print("✅ Base de datos ya existe")

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
