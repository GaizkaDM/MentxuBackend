# ==============================================================================
# 📊 MODELO DE SESIONES - Registro de Login de Usuarios
# ==============================================================================
#
# Registra cada sesión de usuario en la aplicación:
#   - Fecha/hora de inicio y fin
#   - Tipo de dispositivo
#   - Duración de la sesión
#   - IP y user agent (para análisis)
#
# ==============================================================================

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from app import db
from .base import EstadisticaBase


class TipoDispositivo(Enum):
    """Enumeración de tipos de dispositivo."""
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    TABLET = "tablet"
    DESCONOCIDO = "desconocido"


class EstadoSesion(Enum):
    """Estados posibles de una sesión."""
    ACTIVA = "activa"
    CERRADA = "cerrada"
    EXPIRADA = "expirada"


class Sesion(EstadisticaBase):
    """
    Modelo para registrar las sesiones de usuario (login/logout).
    
    Hereda de EstadisticaBase que proporciona:
        - id, fecha_creacion, fecha_actualizacion (de BaseModel)
        - usuario_id, activo (de EstadisticaBase)
    
    Atributos específicos:
        - token_sesion: Identificador único de la sesión
        - fecha_inicio: Momento del login
        - fecha_fin: Momento del logout (null si activa)
        - tipo_dispositivo: Android, iOS, Web, etc.
        - device_info: Información del dispositivo
        - direccion_ip: IP del cliente
        - user_agent: Navegador/App usada
        - estado: activa, cerrada, expirada
        - duracion_segundos: Duración total calculada
    
    Relaciones:
        - usuario: Relación con Usuario (heredado)
    
    Ejemplo de uso:
        # Crear una nueva sesión
        sesion = Sesion(
            usuario_id=1,
            tipo_dispositivo=TipoDispositivo.ANDROID,
            device_info="Samsung Galaxy S21"
        )
        sesion.save()
        
        # Cerrar la sesión
        sesion.cerrar()
    """
    
    __tablename__ = 'sesiones'
    
    # Excluir campos sensibles de la serialización
    _exclude_fields = ['direccion_ip', 'user_agent']
    
    # Campos para resumen
    _summary_fields = ['id', 'usuario_id', 'fecha_inicio', 'estado', 'duracion_segundos']
    
    # -----------------------------
    # Campos específicos de Sesion
    # -----------------------------
    
    token_sesion = db.Column(
        db.String(256),
        unique=True,
        nullable=True,
        index=True,
        doc="Token único de la sesión para validación"
    )
    
    fecha_inicio = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        doc="Fecha y hora de inicio de sesión"
    )
    
    fecha_fin = db.Column(
        db.DateTime,
        nullable=True,
        doc="Fecha y hora de cierre de sesión"
    )
    
    tipo_dispositivo = db.Column(
        db.Enum(TipoDispositivo),
        default=TipoDispositivo.DESCONOCIDO,
        nullable=False,
        doc="Tipo de dispositivo usado"
    )
    
    device_info = db.Column(
        db.String(500),
        nullable=True,
        doc="Información adicional del dispositivo"
    )
    
    direccion_ip = db.Column(
        db.String(45),
        nullable=True,
        doc="Dirección IP del cliente"
    )
    
    user_agent = db.Column(
        db.String(500),
        nullable=True,
        doc="User agent del navegador/app"
    )
    
    estado = db.Column(
        db.Enum(EstadoSesion),
        default=EstadoSesion.ACTIVA,
        nullable=False,
        index=True,
        doc="Estado actual de la sesión"
    )
    
    duracion_segundos = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Duración de la sesión en segundos"
    )
    
    # -----------------------------
    # Relación con Usuario
    # -----------------------------
    
    # Nota: La relación se define con primaryjoin explícito porque
    # usuario_id está definido en la clase padre EstadisticaBase
    usuario = db.relationship(
        'Usuario',
        backref=db.backref('sesiones', lazy='dynamic'),
        primaryjoin='Sesion.usuario_id == Usuario.id'
    )
    
    # -----------------------------
    # Métodos de instancia
    # -----------------------------
    
    def __repr__(self) -> str:
        return f"<Sesion id={self.id} usuario={self.usuario_id} estado={self.estado.value}>"
    
    def cerrar(self) -> 'Sesion':
        """
        Cierra la sesión actual y calcula la duración.
        
        Returns:
            Self para encadenamiento
        """
        if self.estado == EstadoSesion.ACTIVA:
            self.fecha_fin = datetime.utcnow()
            self.estado = EstadoSesion.CERRADA
            self.duracion_segundos = int(
                (self.fecha_fin - self.fecha_inicio).total_seconds()
            )
            db.session.commit()
        
        return self
    
    def expirar(self) -> 'Sesion':
        """
        Marca la sesión como expirada (timeout).
        """
        if self.estado == EstadoSesion.ACTIVA:
            self.fecha_fin = datetime.utcnow()
            self.estado = EstadoSesion.EXPIRADA
            self.duracion_segundos = int(
                (self.fecha_fin - self.fecha_inicio).total_seconds()
            )
            db.session.commit()
        
        return self
    
    def esta_activa(self) -> bool:
        """Verifica si la sesión está activa."""
        return self.estado == EstadoSesion.ACTIVA
    
    def get_duracion_formateada(self) -> str:
        """
        Devuelve la duración en formato legible.
        
        Returns:
            String como "2h 30m 15s"
        """
        segundos = self.duracion_segundos
        
        if self.estado == EstadoSesion.ACTIVA:
            # Calcular duración actual
            segundos = int((datetime.utcnow() - self.fecha_inicio).total_seconds())
        
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60
        
        if horas > 0:
            return f"{horas}h {minutos}m {segs}s"
        elif minutos > 0:
            return f"{minutos}m {segs}s"
        else:
            return f"{segs}s"
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Sobrescribe serialización para incluir campo formateado.
        Ejemplo de polimorfismo.
        """
        data = super().to_dict(include_relations)
        data['duracion_formateada'] = self.get_duracion_formateada()
        data['tipo_dispositivo'] = self.tipo_dispositivo.value
        data['estado'] = self.estado.value
        return data
    
    # -----------------------------
    # Métodos de clase (consultas)
    # -----------------------------
    
    @classmethod
    def crear_sesion(
        cls,
        usuario_id: int,
        tipo_dispositivo: TipoDispositivo = TipoDispositivo.DESCONOCIDO,
        device_info: str = None,
        ip: str = None,
        user_agent: str = None
    ) -> 'Sesion':
        """
        Crea una nueva sesión para el usuario.
        
        Args:
            usuario_id: ID del usuario
            tipo_dispositivo: Tipo de dispositivo
            device_info: Información adicional
            ip: Dirección IP
            user_agent: User agent
            
        Returns:
            Nueva sesión creada y guardada
        """
        import secrets
        
        sesion = cls(
            usuario_id=usuario_id,
            token_sesion=secrets.token_urlsafe(32),
            tipo_dispositivo=tipo_dispositivo,
            device_info=device_info,
            direccion_ip=ip,
            user_agent=user_agent
        )
        
        return sesion.save()
    
    @classmethod
    def get_sesiones_activas(cls, usuario_id: int = None) -> List['Sesion']:
        """
        Obtiene las sesiones activas.
        
        Args:
            usuario_id: Opcional, filtrar por usuario
            
        Returns:
            Lista de sesiones activas
        """
        query = cls.query.filter_by(estado=EstadoSesion.ACTIVA)
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        return query.order_by(cls.fecha_inicio.desc()).all()
    
    @classmethod
    def cerrar_sesiones_antiguas(cls, horas: int = 24) -> int:
        """
        Expira sesiones inactivas por más de X horas.
        
        Args:
            horas: Número de horas de inactividad
            
        Returns:
            Número de sesiones expiradas
        """
        limite = datetime.utcnow() - timedelta(hours=horas)
        
        sesiones = cls.query.filter(
            cls.estado == EstadoSesion.ACTIVA,
            cls.fecha_inicio < limite
        ).all()
        
        count = 0
        for sesion in sesiones:
            sesion.expirar()
            count += 1
        
        return count
    
    @classmethod
    def get_estadisticas_usuario(cls, usuario_id: int) -> Dict[str, Any]:
        """
        Implementación del método abstracto de EstadisticaBase.
        Calcula estadísticas de sesiones para un usuario.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con estadísticas de sesiones
        """
        from sqlalchemy import func
        
        sesiones = cls.query.filter_by(usuario_id=usuario_id)
        
        # Total de sesiones
        total = sesiones.count()
        
        # Sesión más larga
        max_duracion = sesiones.with_entities(
            func.max(cls.duracion_segundos)
        ).scalar() or 0
        
        # Tiempo total de uso
        tiempo_total = sesiones.with_entities(
            func.sum(cls.duracion_segundos)
        ).scalar() or 0
        
        # Promedio de duración
        promedio = sesiones.with_entities(
            func.avg(cls.duracion_segundos)
        ).scalar() or 0
        
        # Última sesión
        ultima_sesion = sesiones.order_by(
            cls.fecha_inicio.desc()
        ).first()
        
        # Dispositivo más usado
        dispositivo_frecuente = db.session.query(
            cls.tipo_dispositivo,
            func.count(cls.id).label('total')
        ).filter_by(usuario_id=usuario_id).group_by(
            cls.tipo_dispositivo
        ).order_by(func.count(cls.id).desc()).first()
        
        return {
            'total_sesiones': total,
            'tiempo_total_segundos': tiempo_total,
            'tiempo_total_formateado': cls._formatear_tiempo(tiempo_total),
            'duracion_maxima_segundos': max_duracion,
            'duracion_maxima_formateada': cls._formatear_tiempo(max_duracion),
            'duracion_promedio_segundos': int(promedio),
            'duracion_promedio_formateada': cls._formatear_tiempo(int(promedio)),
            'ultima_sesion': ultima_sesion.to_dict() if ultima_sesion else None,
            'dispositivo_mas_usado': dispositivo_frecuente[0].value if dispositivo_frecuente else None
        }
    
    @staticmethod
    def _formatear_tiempo(segundos: int) -> str:
        """Formatea segundos a string legible."""
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60
        
        if horas > 0:
            return f"{horas}h {minutos}m"
        elif minutos > 0:
            return f"{minutos}m {segs}s"
        else:
            return f"{segs}s"
    
    @classmethod
    def get_estadisticas_generales(cls) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de todas las sesiones.
        """
        from sqlalchemy import func
        
        return {
            'total_sesiones': cls.query.count(),
            'sesiones_activas': cls.query.filter_by(estado=EstadoSesion.ACTIVA).count(),
            'tiempo_total_uso': cls.query.with_entities(
                func.sum(cls.duracion_segundos)
            ).scalar() or 0,
            'sesiones_hoy': cls.query.filter(
                func.date(cls.fecha_inicio) == datetime.utcnow().date()
            ).count(),
            'sesiones_ultima_semana': cls.query.filter(
                cls.fecha_inicio >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
