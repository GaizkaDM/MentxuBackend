# ==============================================================================
# 📊 MODELO DE LOGROS - Sistema de Achievements
# ==============================================================================
#
# Sistema gamificado de logros para motivar a los usuarios:
#   - Logros definidos por tipo (velocidad, precisión, constancia, etc.)
#   - Seguimiento de progreso hacia cada logro
#   - Desbloqueo automático cuando se cumplen condiciones
#   - Sistema de puntos y niveles
#
# ==============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from app import db
from .base import BaseModel, EstadisticaBase


class TipoLogro(Enum):
    """Categorías de logros disponibles."""
    VELOCIDAD = "velocidad"       # Completar en tiempo récord
    PRECISION = "precision"       # Alta puntuación
    CONSTANCIA = "constancia"     # Uso diario
    EXPLORACION = "exploracion"   # Visitar todas las paradas
    MAESTRIA = "maestria"         # Completar todo el recorrido
    SOCIAL = "social"             # Logros compartidos
    SECRETO = "secreto"           # Logros ocultos
    COLECCIONISTA = "coleccionista"  # Conseguir X logros


class NivelDificultad(Enum):
    """Dificultad del logro (afecta los puntos)."""
    FACIL = "facil"        # 10 puntos
    MEDIO = "medio"        # 25 puntos
    DIFICIL = "dificil"    # 50 puntos
    EXPERTO = "experto"    # 100 puntos
    LEGENDARIO = "legendario"  # 250 puntos


# Puntos por nivel de dificultad
PUNTOS_POR_NIVEL = {
    NivelDificultad.FACIL: 10,
    NivelDificultad.MEDIO: 25,
    NivelDificultad.DIFICIL: 50,
    NivelDificultad.EXPERTO: 100,
    NivelDificultad.LEGENDARIO: 250
}


class Logro(BaseModel):
    """
    Modelo que define los logros disponibles en el sistema.
    
    Representa la "plantilla" de un logro, no la instancia conseguida
    por un usuario específico (eso es LogroUsuario).
    
    Atributos:
        - nombre: Nombre del logro
        - nombre_corto: Código identificador
        - descripcion: Descripción para el usuario
        - tipo: Categoría del logro
        - dificultad: Nivel de dificultad
        - puntos: Puntos que otorga
        - icono: URL o nombre del icono
        - requisitos: JSON con condiciones para desbloquear
        - secreto: Si es un logro oculto
        - orden: Para ordenar en la UI
    
    Ejemplo:
        logro = Logro(
            nombre="Velocista",
            descripcion="Completa una parada en menos de 30 segundos",
            tipo=TipoLogro.VELOCIDAD,
            dificultad=NivelDificultad.MEDIO,
            requisitos={"tiempo_maximo": 30, "paradas_completadas": 1}
        )
    """
    
    __tablename__ = 'logros'
    
    _summary_fields = ['id', 'nombre', 'tipo', 'puntos', 'secreto']
    
    # -----------------------------
    # Campos del logro
    # -----------------------------
    
    nombre = db.Column(
        db.String(100),
        nullable=False,
        doc="Nombre visible del logro"
    )
    
    nombre_corto = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Código único identificador (ej: 'velocista_bronce')"
    )
    
    descripcion = db.Column(
        db.Text,
        nullable=True,
        doc="Descripción detallada para el usuario"
    )
    
    descripcion_bloqueado = db.Column(
        db.Text,
        nullable=True,
        doc="Descripción cuando el logro está bloqueado (para secretos)"
    )
    
    tipo = db.Column(
        db.Enum(TipoLogro),
        default=TipoLogro.EXPLORACION,
        nullable=False,
        index=True,
        doc="Categoría del logro"
    )
    
    dificultad = db.Column(
        db.Enum(NivelDificultad),
        default=NivelDificultad.FACIL,
        nullable=False,
        doc="Nivel de dificultad"
    )
    
    puntos = db.Column(
        db.Integer,
        default=10,
        nullable=False,
        doc="Puntos que otorga al desbloquearse"
    )
    
    icono = db.Column(
        db.String(200),
        nullable=True,
        doc="URL o nombre del icono"
    )
    
    color = db.Column(
        db.String(7),
        default="#FFD700",
        nullable=False,
        doc="Color del logro en formato hex"
    )
    
    requisitos = db.Column(
        db.JSON,
        nullable=True,
        doc="Condiciones para desbloquear (JSON)"
    )
    
    secreto = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        doc="Si es un logro oculto hasta desbloquearse"
    )
    
    orden = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Orden para mostrar en la UI"
    )
    
    activo = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        doc="Si el logro está disponible"
    )
    
    # -----------------------------
    # Relaciones
    # -----------------------------
    
    usuarios = db.relationship(
        'LogroUsuario',
        back_populates='logro',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # -----------------------------
    # Métodos de instancia
    # -----------------------------
    
    def __repr__(self) -> str:
        return f"<Logro '{self.nombre}' tipo={self.tipo.value}>"
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """Serialización personalizada."""
        data = super().to_dict(include_relations)
        data['tipo'] = self.tipo.value
        data['dificultad'] = self.dificultad.value
        data['total_desbloqueados'] = self.usuarios.count()
        return data
    
    def to_dict_para_usuario(self, desbloqueado: bool = False) -> Dict[str, Any]:
        """
        Versión para mostrar al usuario.
        Si es secreto y no desbloqueado, oculta información.
        """
        if self.secreto and not desbloqueado:
            return {
                'id': self.id,
                'nombre': "???",
                'descripcion': self.descripcion_bloqueado or "Logro secreto",
                'tipo': self.tipo.value,
                'puntos': "?",
                'icono': 'locked',
                'secreto': True,
                'desbloqueado': False
            }
        
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo': self.tipo.value,
            'dificultad': self.dificultad.value,
            'puntos': self.puntos,
            'icono': self.icono,
            'color': self.color,
            'secreto': self.secreto,
            'desbloqueado': desbloqueado
        }
    
    def verificar_requisitos(self, usuario_stats: Dict[str, Any]) -> bool:
        """
        Verifica si el usuario cumple los requisitos para desbloquear.
        
        Args:
            usuario_stats: Diccionario con estadísticas del usuario
            
        Returns:
            True si cumple todos los requisitos
        """
        if not self.requisitos:
            return False
        
        for key, valor_requerido in self.requisitos.items():
            valor_actual = usuario_stats.get(key, 0)
            
            # Soportar diferentes tipos de comparación
            if isinstance(valor_requerido, dict):
                operador = valor_requerido.get('operador', '>=')
                valor = valor_requerido.get('valor', 0)
                
                if operador == '>=' and valor_actual < valor:
                    return False
                elif operador == '<=' and valor_actual > valor:
                    return False
                elif operador == '==' and valor_actual != valor:
                    return False
            else:
                # Por defecto, >=
                if valor_actual < valor_requerido:
                    return False
        
        return True
    
    # -----------------------------
    # Métodos de clase
    # -----------------------------
    
    @classmethod
    def get_por_tipo(cls, tipo: TipoLogro) -> List['Logro']:
        """Obtiene logros de una categoría."""
        return cls.query.filter_by(
            tipo=tipo,
            activo=True
        ).order_by(cls.orden).all()
    
    @classmethod
    def get_todos_visibles(cls) -> List['Logro']:
        """Obtiene todos los logros no secretos."""
        return cls.query.filter_by(
            activo=True,
            secreto=False
        ).order_by(cls.orden).all()
    
    @classmethod
    def crear_logros_predefinidos(cls) -> List['Logro']:
        """
        Crea los logros predefinidos del sistema.
        Útil para inicializar la base de datos.
        """
        logros_data = [
            # Logros de velocidad
            {
                'nombre': 'Velocista Novato',
                'nombre_corto': 'velocista_bronce',
                'descripcion': 'Completa tu primera parada en menos de 2 minutos',
                'tipo': TipoLogro.VELOCIDAD,
                'dificultad': NivelDificultad.FACIL,
                'requisitos': {'tiempo_minimo': 120, 'paradas_completadas': 1},
                'icono': '🥉'
            },
            {
                'nombre': 'Velocista Experto',
                'nombre_corto': 'velocista_plata',
                'descripcion': 'Completa 3 paradas en menos de 1 minuto cada una',
                'tipo': TipoLogro.VELOCIDAD,
                'dificultad': NivelDificultad.MEDIO,
                'requisitos': {'tiempo_minimo': 60, 'paradas_rapidas': 3},
                'icono': '🥈'
            },
            {
                'nombre': 'Rayo',
                'nombre_corto': 'velocista_oro',
                'descripcion': 'Completa todas las paradas en menos de 30 segundos',
                'tipo': TipoLogro.VELOCIDAD,
                'dificultad': NivelDificultad.EXPERTO,
                'requisitos': {'tiempo_minimo': 30, 'todas_paradas_rapidas': True},
                'icono': '⚡',
                'secreto': True
            },
            
            # Logros de precisión
            {
                'nombre': 'Preciso',
                'nombre_corto': 'precision_bronce',
                'descripcion': 'Consigue 100% en una actividad',
                'tipo': TipoLogro.PRECISION,
                'dificultad': NivelDificultad.FACIL,
                'requisitos': {'puntuacion_perfecta': 1},
                'icono': '🎯'
            },
            {
                'nombre': 'Perfeccionista',
                'nombre_corto': 'precision_oro',
                'descripcion': 'Consigue 100% en todas las actividades',
                'tipo': TipoLogro.PRECISION,
                'dificultad': NivelDificultad.DIFICIL,
                'requisitos': {'todas_perfectas': True},
                'icono': '💯'
            },
            
            # Logros de exploración
            {
                'nombre': 'Primer Paso',
                'nombre_corto': 'exploracion_inicio',
                'descripcion': 'Completa tu primera parada',
                'tipo': TipoLogro.EXPLORACION,
                'dificultad': NivelDificultad.FACIL,
                'requisitos': {'paradas_completadas': 1},
                'icono': '👣'
            },
            {
                'nombre': 'Explorador',
                'nombre_corto': 'exploracion_medio',
                'descripcion': 'Completa 3 paradas',
                'tipo': TipoLogro.EXPLORACION,
                'dificultad': NivelDificultad.MEDIO,
                'requisitos': {'paradas_completadas': 3},
                'icono': '🧭'
            },
            {
                'nombre': 'Conquistador de Santurtzi',
                'nombre_corto': 'exploracion_completo',
                'descripcion': 'Completa todas las paradas del recorrido',
                'tipo': TipoLogro.MAESTRIA,
                'dificultad': NivelDificultad.DIFICIL,
                'requisitos': {'paradas_completadas': 6},
                'icono': '🏆',
                'color': '#FFD700'
            },
            
            # Logros de constancia
            {
                'nombre': 'Visitante Frecuente',
                'nombre_corto': 'constancia_semana',
                'descripcion': 'Usa la app 3 días seguidos',
                'tipo': TipoLogro.CONSTANCIA,
                'dificultad': NivelDificultad.MEDIO,
                'requisitos': {'dias_seguidos': 3},
                'icono': '📅'
            },
            {
                'nombre': 'Devoto',
                'nombre_corto': 'constancia_mes',
                'descripcion': 'Usa la app durante 7 días seguidos',
                'tipo': TipoLogro.CONSTANCIA,
                'dificultad': NivelDificultad.EXPERTO,
                'requisitos': {'dias_seguidos': 7},
                'icono': '🔥',
                'secreto': True
            },
            
            # Logro legendario
            {
                'nombre': 'Leyenda de Santurtzi',
                'nombre_corto': 'leyenda',
                'descripcion': 'Consigue todos los demás logros',
                'descripcion_bloqueado': 'Un logro para los más dedicados...',
                'tipo': TipoLogro.COLECCIONISTA,
                'dificultad': NivelDificultad.LEGENDARIO,
                'requisitos': {'todos_logros': True},
                'icono': '👑',
                'color': '#9B59B6',
                'secreto': True
            }
        ]
        
        creados = []
        for data in logros_data:
            # Verificar si ya existe
            existente = cls.query.filter_by(nombre_corto=data['nombre_corto']).first()
            if not existente:
                # Calcular puntos basado en dificultad
                data['puntos'] = PUNTOS_POR_NIVEL[data['dificultad']]
                
                logro = cls(**data)
                db.session.add(logro)
                creados.append(logro)
        
        if creados:
            db.session.commit()
        
        return creados


class LogroUsuario(EstadisticaBase):
    """
    Modelo que registra los logros desbloqueados por cada usuario.
    
    Representa la relación muchos-a-muchos entre Usuario y Logro,
    con información adicional del momento del desbloqueo.
    
    Atributos:
        - usuario_id: ID del usuario (heredado)
        - logro_id: ID del logro desbloqueado
        - fecha_desbloqueo: Cuando se consiguió
        - progreso: Progreso actual (0-100) para logros progresivos
        - notificado: Si ya se notificó al usuario
    
    Ejemplo:
        # Desbloquear un logro
        logro_usuario = LogroUsuario.desbloquear(usuario_id=1, logro_id=5)
    """
    
    __tablename__ = 'logros_usuarios'
    
    # Excluir de serialización básica
    _exclude_fields = []
    
    # Constraint único
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'logro_id', name='unique_usuario_logro'),
    )
    
    # -----------------------------
    # Campos específicos
    # -----------------------------
    
    logro_id = db.Column(
        db.Integer,
        db.ForeignKey('logros.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    fecha_desbloqueo = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    progreso = db.Column(
        db.Integer,
        default=100,
        nullable=False,
        doc="Progreso 0-100 (100 = completado)"
    )
    
    notificado = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        doc="Si se ha notificado al usuario"
    )
    
    # -----------------------------
    # Relaciones
    # -----------------------------
    
    logro = db.relationship(
        'Logro',
        back_populates='usuarios'
    )
    
    usuario = db.relationship(
        'Usuario',
        backref=db.backref('logros_desbloqueados', lazy='dynamic')
    )
    
    # -----------------------------
    # Métodos
    # -----------------------------
    
    def __repr__(self) -> str:
        return f"<LogroUsuario usuario={self.usuario_id} logro={self.logro_id}>"
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        data = super().to_dict(include_relations)
        
        if include_relations and self.logro:
            data['logro'] = self.logro.to_dict()
        
        return data
    
    def marcar_notificado(self) -> 'LogroUsuario':
        """Marca el logro como notificado."""
        self.notificado = True
        db.session.commit()
        return self
    
    @classmethod
    def desbloquear(
        cls,
        usuario_id: int,
        logro_id: int,
        progreso: int = 100
    ) -> Optional['LogroUsuario']:
        """
        Desbloquea un logro para un usuario.
        
        Args:
            usuario_id: ID del usuario
            logro_id: ID del logro
            progreso: Progreso (100 = completado)
            
        Returns:
            LogroUsuario creado o existente, None si no se puede
        """
        # Verificar si ya existe
        existente = cls.query.filter_by(
            usuario_id=usuario_id,
            logro_id=logro_id
        ).first()
        
        if existente:
            # Actualizar progreso si es mayor
            if progreso > existente.progreso:
                existente.progreso = progreso
                if progreso >= 100:
                    existente.fecha_desbloqueo = datetime.utcnow()
                db.session.commit()
            return existente
        
        # Crear nuevo
        logro_usuario = cls(
            usuario_id=usuario_id,
            logro_id=logro_id,
            progreso=progreso
        )
        
        return logro_usuario.save()
    
    @classmethod
    def get_logros_usuario(
        cls,
        usuario_id: int,
        solo_completados: bool = False
    ) -> List['LogroUsuario']:
        """
        Obtiene los logros de un usuario.
        
        Args:
            usuario_id: ID del usuario
            solo_completados: Solo devolver los completados (progreso=100)
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        
        if solo_completados:
            query = query.filter(cls.progreso >= 100)
        
        return query.order_by(cls.fecha_desbloqueo.desc()).all()
    
    @classmethod
    def get_puntos_totales(cls, usuario_id: int) -> int:
        """
        Calcula los puntos totales del usuario por logros.
        """
        from sqlalchemy import func
        
        resultado = db.session.query(
            func.sum(Logro.puntos)
        ).join(cls).filter(
            cls.usuario_id == usuario_id,
            cls.progreso >= 100
        ).scalar()
        
        return resultado or 0
    
    @classmethod
    def get_pendientes_notificar(cls, usuario_id: int) -> List['LogroUsuario']:
        """Obtiene logros pendientes de notificar."""
        return cls.query.filter_by(
            usuario_id=usuario_id,
            notificado=False,
            progreso=100
        ).all()
    
    @classmethod
    def get_estadisticas_usuario(cls, usuario_id: int) -> Dict[str, Any]:
        """
        Estadísticas de logros para un usuario.
        """
        logros_usuario = cls.query.filter_by(usuario_id=usuario_id).all()
        total_logros = Logro.query.filter_by(activo=True).count()
        
        completados = [lu for lu in logros_usuario if lu.progreso >= 100]
        en_progreso = [lu for lu in logros_usuario if lu.progreso < 100]
        
        puntos = sum(lu.logro.puntos for lu in completados if lu.logro)
        
        # Por tipo
        por_tipo = {}
        for tipo in TipoLogro:
            logros_tipo = Logro.query.filter_by(tipo=tipo, activo=True).count()
            completados_tipo = len([
                lu for lu in completados 
                if lu.logro and lu.logro.tipo == tipo
            ])
            por_tipo[tipo.value] = {
                'total': logros_tipo,
                'completados': completados_tipo,
                'porcentaje': (completados_tipo / logros_tipo * 100) if logros_tipo > 0 else 0
            }
        
        return {
            'total_disponibles': total_logros,
            'completados': len(completados),
            'en_progreso': len(en_progreso),
            'porcentaje_completado': (len(completados) / total_logros * 100) if total_logros > 0 else 0,
            'puntos_totales': puntos,
            'por_tipo': por_tipo,
            'ultimos_desbloqueados': [
                lu.to_dict(include_relations=True) 
                for lu in completados[:5]
            ]
        }
