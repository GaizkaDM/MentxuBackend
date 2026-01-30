# ==============================================================================
# 📊 MODELO HISTORIAL DE INTENTOS - Registro Detallado de Actividades
# ==============================================================================
#
# Registra cada intento individual en las actividades:
#   - A diferencia de Progreso (que guarda el estado final),
#     HistorialIntento guarda CADA intento individual
#   - Permite análisis de progreso y mejora del usuario
#   - Base para gráficos de evolución
#
# ==============================================================================

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from app import db
from .base import EstadisticaBase


class ResultadoIntento(Enum):
    """Resultado posible de un intento."""
    EXITO = "exito"
    FALLO = "fallo"
    ABANDONADO = "abandonado"
    TIEMPO_AGOTADO = "tiempo_agotado"


class TipoActividad(Enum):
    """Tipos de actividades/mini-juegos."""
    SOPA_LETRAS = "sopa_letras"
    DIFERENCIAS = "diferencias"
    RELACIONAR = "relacionar"
    RECOGIDA = "recogida"
    PESCA = "pesca"
    PUZZLE = "puzzle"
    OTRO = "otro"


class HistorialIntento(EstadisticaBase):
    """
    Modelo para registrar cada intento individual en una actividad.
    
    Mientras que el modelo Progreso guarda el estado final de una parada,
    HistorialIntento registra CADA intento, permitiendo:
        - Ver evolución del usuario
        - Identificar actividades difíciles
        - Calcular métricas de mejora
        - Generar gráficos de progreso
    
    Atributos heredados:
        - id, fecha_creacion, fecha_actualizacion (BaseModel)
        - usuario_id, activo (EstadisticaBase)
    
    Atributos específicos:
        - parada_id: ID de la parada/actividad
        - tipo_actividad: Tipo de mini-juego
        - numero_intento: Número de intento (1, 2, 3...)
        - puntuacion: Puntuación obtenida (0-100)
        - tiempo_segundos: Tiempo empleado
        - resultado: éxito, fallo, abandonado, etc.
        - errores: Número de errores cometidos
        - pistas_usadas: Número de pistas utilizadas
        - detalles: JSON con información adicional
    
    Ejemplo:
        intento = HistorialIntento(
            usuario_id=1,
            parada_id=2,
            tipo_actividad=TipoActividad.DIFERENCIAS,
            puntuacion=85,
            tiempo_segundos=45,
            resultado=ResultadoIntento.EXITO
        )
    """
    
    __tablename__ = 'historial_intentos'
    
    _summary_fields = [
        'id', 'usuario_id', 'parada_id', 
        'puntuacion', 'resultado', 'fecha_creacion'
    ]
    
    # -----------------------------
    # Campos del intento
    # -----------------------------
    
    parada_id = db.Column(
        db.Integer,
        db.ForeignKey('paradas.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID de la parada/actividad"
    )
    
    tipo_actividad = db.Column(
        db.Enum(TipoActividad),
        default=TipoActividad.OTRO,
        nullable=False,
        index=True,
        doc="Tipo de mini-juego"
    )
    
    numero_intento = db.Column(
        db.Integer,
        default=1,
        nullable=False,
        doc="Número de intento del usuario en esta actividad"
    )
    
    puntuacion = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Puntuación obtenida (0-100)"
    )
    
    tiempo_segundos = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Tiempo empleado en segundos"
    )
    
    resultado = db.Column(
        db.Enum(ResultadoIntento),
        default=ResultadoIntento.EXITO,
        nullable=False,
        index=True,
        doc="Resultado del intento"
    )
    
    errores = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Número de errores cometidos"
    )
    
    pistas_usadas = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        doc="Número de pistas utilizadas"
    )
    
    detalles = db.Column(
        db.JSON,
        nullable=True,
        doc="Información adicional en JSON"
    )
    
    # -----------------------------
    # Relaciones
    # -----------------------------
    
    usuario = db.relationship(
        'Usuario',
        backref=db.backref('intentos', lazy='dynamic'),
        primaryjoin='HistorialIntento.usuario_id == Usuario.id'
    )
    
    parada = db.relationship(
        'Parada',
        backref=db.backref('intentos', lazy='dynamic'),
        primaryjoin='HistorialIntento.parada_id == Parada.id'
    )
    
    # -----------------------------
    # Métodos de instancia
    # -----------------------------
    
    def __repr__(self) -> str:
        return (
            f"<HistorialIntento usuario={self.usuario_id} "
            f"parada={self.parada_id} intento={self.numero_intento}>"
        )
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """Serialización con campos adicionales."""
        data = super().to_dict(include_relations)
        data['tipo_actividad'] = self.tipo_actividad.value
        data['resultado'] = self.resultado.value
        data['tiempo_formateado'] = self._formatear_tiempo(self.tiempo_segundos)
        
        if include_relations:
            if self.parada:
                data['parada_nombre'] = self.parada.nombre_corto
        
        return data
    
    def es_exitoso(self) -> bool:
        """Verifica si el intento fue exitoso."""
        return self.resultado == ResultadoIntento.EXITO
    
    def es_perfecto(self) -> bool:
        """Verifica si fue puntuación perfecta sin errores ni pistas."""
        return (
            self.puntuacion == 100 and 
            self.errores == 0 and 
            self.pistas_usadas == 0
        )
    
    @staticmethod
    def _formatear_tiempo(segundos: int) -> str:
        """Formatea segundos a string legible."""
        minutos = segundos // 60
        segs = segundos % 60
        
        if minutos > 0:
            return f"{minutos}m {segs}s"
        else:
            return f"{segs}s"
    
    # -----------------------------
    # Métodos de clase (Factory)
    # -----------------------------
    
    @classmethod
    def registrar_intento(
        cls,
        usuario_id: int,
        parada_id: int,
        tipo_actividad: TipoActividad,
        puntuacion: int,
        tiempo_segundos: int,
        resultado: ResultadoIntento = ResultadoIntento.EXITO,
        errores: int = 0,
        pistas_usadas: int = 0,
        detalles: Dict = None
    ) -> 'HistorialIntento':
        """
        Factory method para registrar un nuevo intento.
        Calcula automáticamente el número de intento.
        
        Args:
            usuario_id: ID del usuario
            parada_id: ID de la parada
            tipo_actividad: Tipo de mini-juego
            puntuacion: Puntuación obtenida
            tiempo_segundos: Tiempo empleado
            resultado: Resultado del intento
            errores: Número de errores
            pistas_usadas: Pistas utilizadas
            detalles: Info adicional
            
        Returns:
            Nuevo HistorialIntento guardado
        """
        # Calcular número de intento
        intentos_anteriores = cls.query.filter_by(
            usuario_id=usuario_id,
            parada_id=parada_id
        ).count()
        
        intento = cls(
            usuario_id=usuario_id,
            parada_id=parada_id,
            tipo_actividad=tipo_actividad,
            numero_intento=intentos_anteriores + 1,
            puntuacion=puntuacion,
            tiempo_segundos=tiempo_segundos,
            resultado=resultado,
            errores=errores,
            pistas_usadas=pistas_usadas,
            detalles=detalles
        )
        
        return intento.save()
    
    # -----------------------------
    # Consultas estadísticas
    # -----------------------------
    
    @classmethod
    def get_intentos_usuario(
        cls,
        usuario_id: int,
        parada_id: int = None,
        limite: int = None
    ) -> List['HistorialIntento']:
        """
        Obtiene el historial de intentos de un usuario.
        
        Args:
            usuario_id: ID del usuario
            parada_id: Opcional, filtrar por parada
            limite: Máximo de resultados
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        
        if parada_id:
            query = query.filter_by(parada_id=parada_id)
        
        query = query.order_by(cls.fecha_creacion.desc())
        
        if limite:
            query = query.limit(limite)
        
        return query.all()
    
    @classmethod
    def get_mejor_intento(
        cls,
        usuario_id: int,
        parada_id: int
    ) -> Optional['HistorialIntento']:
        """
        Obtiene el mejor intento del usuario en una parada.
        Considera puntuación, luego tiempo.
        """
        return cls.query.filter_by(
            usuario_id=usuario_id,
            parada_id=parada_id,
            resultado=ResultadoIntento.EXITO
        ).order_by(
            cls.puntuacion.desc(),
            cls.tiempo_segundos.asc()
        ).first()
    
    @classmethod
    def get_evolucion_usuario(
        cls,
        usuario_id: int,
        parada_id: int = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la evolución del usuario (para gráficos).
        
        Returns:
            Lista de diccionarios con puntuación por intento
        """
        query = cls.query.filter_by(usuario_id=usuario_id)
        
        if parada_id:
            query = query.filter_by(parada_id=parada_id)
        
        intentos = query.order_by(
            cls.parada_id,
            cls.numero_intento
        ).all()
        
        return [
            {
                'intento': i.numero_intento,
                'parada_id': i.parada_id,
                'puntuacion': i.puntuacion,
                'tiempo': i.tiempo_segundos,
                'fecha': i.fecha_creacion.isoformat()
            }
            for i in intentos
        ]
    
    @classmethod
    def get_estadisticas_usuario(cls, usuario_id: int) -> Dict[str, Any]:
        """
        Implementación del método abstracto de EstadisticaBase.
        Calcula estadísticas detalladas de intentos.
        """
        from sqlalchemy import func
        
        intentos = cls.query.filter_by(usuario_id=usuario_id)
        
        # Básicas
        total = intentos.count()
        exitosos = intentos.filter_by(resultado=ResultadoIntento.EXITO).count()
        fallidos = intentos.filter_by(resultado=ResultadoIntento.FALLO).count()
        
        # Promedios
        promedio_puntuacion = intentos.with_entities(
            func.avg(cls.puntuacion)
        ).scalar() or 0
        
        promedio_tiempo = intentos.with_entities(
            func.avg(cls.tiempo_segundos)
        ).scalar() or 0
        
        # Mejor puntuación
        mejor_puntuacion = intentos.with_entities(
            func.max(cls.puntuacion)
        ).scalar() or 0
        
        # Tiempo más rápido (de los exitosos)
        tiempo_rapido = intentos.filter_by(
            resultado=ResultadoIntento.EXITO
        ).with_entities(
            func.min(cls.tiempo_segundos)
        ).scalar() or 0
        
        # Intentos perfectos
        perfectos = intentos.filter(
            cls.puntuacion == 100,
            cls.errores == 0,
            cls.pistas_usadas == 0
        ).count()
        
        # Por tipo de actividad
        por_tipo = {}
        for tipo in TipoActividad:
            intentos_tipo = intentos.filter_by(tipo_actividad=tipo).count()
            exitosos_tipo = intentos.filter_by(
                tipo_actividad=tipo,
                resultado=ResultadoIntento.EXITO
            ).count()
            
            por_tipo[tipo.value] = {
                'total': intentos_tipo,
                'exitosos': exitosos_tipo,
                'tasa_exito': (exitosos_tipo / intentos_tipo * 100) if intentos_tipo > 0 else 0
            }
        
        return {
            'total_intentos': total,
            'exitosos': exitosos,
            'fallidos': fallidos,
            'tasa_exito': (exitosos / total * 100) if total > 0 else 0,
            'puntuacion_promedio': round(promedio_puntuacion, 2),
            'tiempo_promedio_segundos': round(promedio_tiempo, 2),
            'mejor_puntuacion': mejor_puntuacion,
            'tiempo_mas_rapido': tiempo_rapido,
            'intentos_perfectos': perfectos,
            'por_tipo_actividad': por_tipo
        }
    
    @classmethod
    def get_estadisticas_parada(cls, parada_id: int) -> Dict[str, Any]:
        """
        Estadísticas de una parada específica (todos los usuarios).
        """
        from sqlalchemy import func
        
        intentos = cls.query.filter_by(parada_id=parada_id)
        
        total = intentos.count()
        exitosos = intentos.filter_by(resultado=ResultadoIntento.EXITO).count()
        
        promedio_puntuacion = intentos.with_entities(
            func.avg(cls.puntuacion)
        ).scalar() or 0
        
        promedio_tiempo = intentos.with_entities(
            func.avg(cls.tiempo_segundos)
        ).scalar() or 0
        
        # Usuarios únicos
        usuarios_unicos = intentos.with_entities(
            func.count(func.distinct(cls.usuario_id))
        ).scalar() or 0
        
        # Distribución de puntuaciones
        rangos = {
            '0-25': 0,
            '26-50': 0,
            '51-75': 0,
            '76-100': 0
        }
        
        for intento in intentos.all():
            if intento.puntuacion <= 25:
                rangos['0-25'] += 1
            elif intento.puntuacion <= 50:
                rangos['26-50'] += 1
            elif intento.puntuacion <= 75:
                rangos['51-75'] += 1
            else:
                rangos['76-100'] += 1
        
        return {
            'parada_id': parada_id,
            'total_intentos': total,
            'tasa_exito': (exitosos / total * 100) if total > 0 else 0,
            'puntuacion_promedio': round(promedio_puntuacion, 2),
            'tiempo_promedio_segundos': round(promedio_tiempo, 2),
            'usuarios_unicos': usuarios_unicos,
            'distribucion_puntuaciones': rangos
        }
    
    @classmethod
    def get_estadisticas_generales(cls) -> Dict[str, Any]:
        """
        Estadísticas generales de todas las actividades.
        """
        from sqlalchemy import func
        
        total = cls.query.count()
        
        # Actividad más jugada
        actividad_popular = db.session.query(
            cls.tipo_actividad,
            func.count(cls.id).label('total')
        ).group_by(cls.tipo_actividad).order_by(
            func.count(cls.id).desc()
        ).first()
        
        # Parada más difícil (menor tasa de éxito)
        stats_paradas = db.session.query(
            cls.parada_id,
            func.count(cls.id).label('total'),
            func.sum(
                db.case(
                    (cls.resultado == ResultadoIntento.EXITO, 1),
                    else_=0
                )
            ).label('exitosos')
        ).group_by(cls.parada_id).all()
        
        parada_dificil = None
        menor_tasa = 100
        for stat in stats_paradas:
            if stat.total >= 10:  # Mínimo 10 intentos
                tasa = (stat.exitosos / stat.total * 100)
                if tasa < menor_tasa:
                    menor_tasa = tasa
                    parada_dificil = stat.parada_id
        
        # Intentos hoy
        hoy = datetime.utcnow().date()
        intentos_hoy = cls.query.filter(
            func.date(cls.fecha_creacion) == hoy
        ).count()
        
        return {
            'total_intentos': total,
            'actividad_mas_jugada': actividad_popular[0].value if actividad_popular else None,
            'parada_mas_dificil_id': parada_dificil,
            'intentos_hoy': intentos_hoy,
            'intentos_ultima_semana': cls.query.filter(
                cls.fecha_creacion >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
