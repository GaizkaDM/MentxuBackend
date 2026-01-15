from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login"""
    return Admin.query.get(int(user_id))


class Admin(UserMixin, db.Model):
    """Modelo para usuarios administradores del panel web"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Usuario(db.Model):
    """Modelo para usuarios de la app móvil"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.String(200), unique=True)  # Identificador único del dispositivo
    
    # Relación con progreso
    progresos = db.relationship('Progreso', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'device_id': self.device_id
        }


class Parada(db.Model):
    """Modelo para las paradas del recorrido turístico"""
    __tablename__ = 'paradas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    nombre_corto = db.Column(db.String(100))  # Ej: "El Ayuntamiento"
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)
    tipo_juego = db.Column(db.String(50))  # 'sopa_letras', 'diferencias', 'relacionar', etc.
    orden = db.Column(db.Integer, unique=True)  # Orden en el recorrido
    imagen_url = db.Column(db.String(300))  # URL o path de la imagen
    
    # Relación con progreso
    progresos = db.relationship('Progreso', backref='parada', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Parada {self.orden}: {self.nombre_corto}>'
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nombre_corto': self.nombre_corto,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'descripcion': self.descripcion,
            'tipo_juego': self.tipo_juego,
            'orden': self.orden,
            'imagen_url': self.imagen_url
        }


class Progreso(db.Model):
    """Modelo para el progreso de cada usuario en cada parada"""
    __tablename__ = 'progreso'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    parada_id = db.Column(db.Integer, db.ForeignKey('paradas.id'), nullable=False)
    
    # Estados: 'bloqueada', 'activa', 'completada'
    estado = db.Column(db.String(20), default='bloqueada')
    
    fecha_inicio = db.Column(db.DateTime)  # Cuando se activó
    fecha_completado = db.Column(db.DateTime)  # Cuando se completó
    
    # Métricas opcionales
    puntuacion = db.Column(db.Integer, default=0)
    tiempo_empleado = db.Column(db.Integer)  # Segundos
    intentos = db.Column(db.Integer, default=0)
    
    # Constraint único: un usuario solo puede tener un progreso por parada
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'parada_id', name='unique_usuario_parada'),
    )
    
    def __repr__(self):
        return f'<Progreso Usuario:{self.usuario_id} Parada:{self.parada_id} Estado:{self.estado}>'
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'parada_id': self.parada_id,
            'estado': self.estado,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_completado': self.fecha_completado.isoformat() if self.fecha_completado else None,
            'puntuacion': self.puntuacion,
            'tiempo_empleado': self.tiempo_empleado,
            'intentos': self.intentos
        }
