# ==============================================================================
# 📊 CLASES BASE - POO con Herencia y Polimorfismo
# ==============================================================================
#
# Este módulo implementa patrones avanzados de POO:
#   - Mixins para funcionalidad compartida
#   - Clase base abstracta para modelos
#   - Métodos polimórficos (to_dict, to_csv_row, etc.)
#
# ==============================================================================

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from app import db


class TimestampMixin:
    """
    Mixin que añade campos de timestamp automáticos.
    
    Proporciona:
        - fecha_creacion: Se establece al crear el registro
        - fecha_actualizacion: Se actualiza automáticamente al modificar
    
    Ejemplo de uso:
        class MiModelo(db.Model, TimestampMixin):
            id = db.Column(db.Integer, primary_key=True)
            nombre = db.Column(db.String(100))
    """
    
    fecha_creacion = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        nullable=False,
        doc="Fecha y hora de creación del registro"
    )
    
    fecha_actualizacion = db.Column(
        db.DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Fecha y hora de última actualización"
    )


class DictSerializableMixin:
    """
    Mixin que proporciona métodos de serialización.
    
    Implementa el patrón de polimorfismo, permitiendo que cada
    clase hija personalice cómo se serializa a diferentes formatos.
    """
    
    # Campos a excluir de la serialización por defecto
    _exclude_fields: List[str] = []
    
    # Campos a incluir en el resumen
    _summary_fields: List[str] = []
    
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Serializa el modelo a un diccionario.
        
        Args:
            include_relations: Si incluir relaciones anidadas
            
        Returns:
            Diccionario con los datos del modelo
            
        Nota: Las subclases pueden sobrescribir este método para
        personalizar la serialización (polimorfismo).
        """
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in self._exclude_fields:
                value = getattr(self, column.name)
                
                # Convertir tipos especiales
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, 'value'):  # Para Enums
                    value = value.value
                    
                result[column.name] = value
        
        return result
    
    def to_summary(self) -> Dict[str, Any]:
        """
        Devuelve un resumen con los campos principales.
        Útil para listados y búsquedas rápidas.
        """
        if not self._summary_fields:
            return self.to_dict()
        
        return {
            field: getattr(self, field, None) 
            for field in self._summary_fields
        }
    
    def to_csv_row(self) -> List[Any]:
        """
        Devuelve una fila para exportación CSV.
        
        Returns:
            Lista de valores en el orden de las columnas
        """
        return [
            getattr(self, col.name) 
            for col in self.__table__.columns
            if col.name not in self._exclude_fields
        ]
    
    @classmethod
    def get_csv_headers(cls) -> List[str]:
        """
        Devuelve los encabezados para CSV.
        """
        return [
            col.name 
            for col in cls.__table__.columns
            if col.name not in cls._exclude_fields
        ]


class BaseModel(db.Model, TimestampMixin, DictSerializableMixin):
    """
    Clase base abstracta para todos los modelos de estadísticas.
    
    Proporciona:
        - ID auto-generado
        - Timestamps automáticos
        - Métodos de serialización
        - Métodos de consulta comunes
    
    Esta clase implementa el patrón Template Method, donde define
    la estructura general y las subclases implementan los detalles.
    
    Ejemplo:
        class Sesion(BaseModel):
            __tablename__ = 'sesiones'
            usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    """
    
    __abstract__ = True  # No crear tabla para esta clase base
    
    id = db.Column(
        db.Integer, 
        primary_key=True,
        doc="Identificador único auto-generado"
    )
    
    # Campos a excluir de la serialización (password_hash, etc.)
    _exclude_fields: List[str] = []
    
    def __repr__(self) -> str:
        """Representación legible del modelo."""
        return f"<{self.__class__.__name__} id={self.id}>"
    
    def save(self) -> 'BaseModel':
        """
        Guarda el modelo en la base de datos.
        
        Returns:
            Self para permitir encadenamiento
            
        Raises:
            SQLAlchemyError: Si hay error en la operación
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self) -> None:
        """
        Elimina el modelo de la base de datos.
        """
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs) -> 'BaseModel':
        """
        Actualiza campos del modelo.
        
        Args:
            **kwargs: Campos a actualizar con sus nuevos valores
            
        Returns:
            Self para permitir encadenamiento
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.commit()
        return self
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional['BaseModel']:
        """
        Obtiene un modelo por su ID.
        
        Args:
            id: ID del registro a buscar
            
        Returns:
            Instancia del modelo o None
        """
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls, limit: int = None, offset: int = 0) -> List['BaseModel']:
        """
        Obtiene todos los registros con paginación opcional.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de registros a saltar
            
        Returns:
            Lista de instancias del modelo
        """
        query = cls.query.order_by(cls.id)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    @classmethod
    def count(cls) -> int:
        """
        Cuenta el total de registros.
        """
        return cls.query.count()
    
    @classmethod
    def filter_by_date_range(
        cls, 
        fecha_inicio: datetime,
        fecha_fin: datetime,
        campo: str = 'fecha_creacion'
    ) -> List['BaseModel']:
        """
        Filtra registros por rango de fechas.
        
        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            campo: Campo de fecha a filtrar (por defecto fecha_creacion)
            
        Returns:
            Lista de registros en el rango
        """
        campo_db = getattr(cls, campo, None)
        
        if campo_db is None:
            raise ValueError(f"El campo '{campo}' no existe en {cls.__name__}")
        
        return cls.query.filter(
            campo_db >= fecha_inicio,
            campo_db <= fecha_fin
        ).order_by(campo_db).all()


class EstadisticaBase(BaseModel):
    """
    Clase base para modelos de estadísticas específicos.
    
    Añade campos comunes a todas las estadísticas:
        - usuario_id: Relación con el usuario
        - activo: Si el registro está activo
    
    Esta clase demuestra herencia multinivel (EstadisticaBase → BaseModel → db.Model)
    """
    
    __abstract__ = True
    
    # Campos comunes
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        doc="ID del usuario asociado"
    )
    
    activo = db.Column(
        db.Boolean, 
        default=True,
        nullable=False,
        doc="Si el registro está activo"
    )
    
    @classmethod
    def get_by_usuario(cls, usuario_id: int) -> List['EstadisticaBase']:
        """
        Obtiene todos los registros de un usuario específico.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de registros del usuario
        """
        return cls.query.filter_by(
            usuario_id=usuario_id,
            activo=True
        ).order_by(cls.fecha_creacion.desc()).all()
    
    @classmethod
    def get_estadisticas_usuario(cls, usuario_id: int) -> Dict[str, Any]:
        """
        Método abstracto que debe ser implementado por las subclases.
        Cada tipo de estadística define cómo calcular sus métricas.
        
        Este es un ejemplo de polimorfismo, donde cada subclase
        proporcionará su propia implementación.
        """
        raise NotImplementedError(
            "Subclases deben implementar get_estadisticas_usuario()"
        )
