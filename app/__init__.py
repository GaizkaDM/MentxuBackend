from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

try:
    from flask_babel import Babel
    babel = Babel()
except ImportError:
    print("⚠️ Flask-Babel no instalado, traducciones desactivadas")
    babel = None

def get_locale():
    """Determina el idioma del usuario"""
    # 1. Parámetro URL ?lang=xx
    lang = request.args.get('lang')
    if lang and lang in ['es', 'eu', 'en']:
        session['lang'] = lang
        return lang
    # 2. Sesión guardada
    if 'lang' in session:
        return session['lang']
    # 3. Accept-Language header
    return request.accept_languages.best_match(['es', 'eu', 'en'], default='es')

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
        
        # MIGRACIÓN: Verificar y añadir columnas avatar y color_favorito si no existen
        if is_postgres:
            try:
                from sqlalchemy import text
                # Verificar si existe la columna avatar
                result = db.session.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'usuarios' AND column_name = 'avatar'"
                ))
                if result.fetchone() is None:
                    print("🔄 Añadiendo columna 'avatar' a tabla usuarios...")
                    db.session.execute(text(
                        "ALTER TABLE usuarios ADD COLUMN avatar VARCHAR(50) DEFAULT 'perro'"
                    ))
                    db.session.commit()
                    print("✅ Columna 'avatar' añadida")
                
                # Verificar si existe la columna color_favorito
                result = db.session.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'usuarios' AND column_name = 'color_favorito'"
                ))
                if result.fetchone() is None:
                    print("🔄 Añadiendo columna 'color_favorito' a tabla usuarios...")
                    db.session.execute(text(
                        "ALTER TABLE usuarios ADD COLUMN color_favorito VARCHAR(20) DEFAULT 'azul'"
                    ))
                    db.session.commit()
                    print("✅ Columna 'color_favorito' añadida")
            except Exception as e:
                print(f"⚠️ Error en migración de columnas: {e}")
                db.session.rollback()
        
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
    
    # Inicializar Babel si está disponible
    if babel is not None:
        babel.init_app(app, locale_selector=get_locale)
        print("✅ Flask-Babel inicializado")
    else:
        # Fallback: _ simplemente devuelve el texto sin traducir
        app.jinja_env.globals['_'] = lambda x: x
    
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
    
    # Inicializar módulo de estadísticas
    try:
        from app.estadisticas import init_estadisticas
        init_estadisticas(app, db)
        print("✅ Módulo de estadísticas cargado")
    except ImportError as e:
        print(f"⚠️ Módulo de estadísticas no disponible: {e}")
    
    return app
