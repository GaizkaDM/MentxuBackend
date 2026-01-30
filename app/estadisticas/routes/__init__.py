# ==============================================================================
# 📊 RUTAS DEL MÓDULO DE ESTADÍSTICAS
# ==============================================================================

from .estadisticas_api import estadisticas_api_bp
from .logros_api import logros_api_bp
from .exportar_api import exportar_api_bp

__all__ = [
    'estadisticas_api_bp',
    'logros_api_bp',
    'exportar_api_bp',
]
