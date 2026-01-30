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
from .sesion import Sesion
from .logro import Logro, LogroUsuario, TipoLogro
from .historial import HistorialIntento

__all__ = [
    # Clases base
    'BaseModel',
    'TimestampMixin', 
    'DictSerializableMixin',
    
    # Modelos de datos
    'Sesion',
    'Logro',
    'LogroUsuario',
    'TipoLogro',
    'HistorialIntento',
]
