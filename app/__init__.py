from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import os

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Crear carpeta instance si no existe
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
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
