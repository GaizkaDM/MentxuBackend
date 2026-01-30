# ==============================================================================
# 📊 MODELOS DE ESTADÍSTICAS - SQLAlchemy ORM
# ==============================================================================
# 
# Este paquete contiene todos los modelos de datos para el sistema de
# estadísticas, implementando:
#   - Herencia de clases base
#   - Relaciones entre tablas
#   - Métodos polimórficos
#
# ==============================================================================

from .base import BaseModel, TimestampMixin, DictSerializableMixin
from .sesion import Sesion, TipoDispositivo, EstadoSesion
from .logro import Logro, LogroUsuario, TipoLogro
from .historial import HistorialIntento, ResultadoIntento, TipoActividad

__all__ = [
    # Clases base
    'BaseModel',
    'TimestampMixin', 
    'DictSerializableMixin',
    
    # Modelos de datos
    'Sesion',
    'TipoDispositivo',
    'EstadoSesion',
    'Logro',
    'LogroUsuario',
    'TipoLogro',
    'HistorialIntento',
    'ResultadoIntento',
    'TipoActividad',
]
