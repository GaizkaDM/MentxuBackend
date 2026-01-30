# ==============================================================================
# 📊 EXPORTADOR JSON - Exportación a JSON con metadatos
# ==============================================================================
#
# Exporta datos a formato JSON usando el módulo nativo de Python.
# Soporta:
#   - Metadatos de exportación
#   - Formato legible (pretty print) o compacto
#   - Serialización de fechas y tipos especiales
#
# ==============================================================================

import json
from datetime import datetime, date
from typing import Dict, List, Any
from enum import Enum
from .base_exporter import (
    BaseExporter,
    ExporterFactory,
    FormatoExportacion,
    FiltroExportacion
)


class JSONEncoder(json.JSONEncoder):
    """
    Encoder JSON personalizado para tipos especiales.
    
    Maneja:
        - datetime → ISO 8601 string
        - date → ISO 8601 string
        - Enum → valor del enum
        - bytes → base64
        - Sets → lista
    """
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if isinstance(obj, date):
            return obj.isoformat()
        
        if isinstance(obj, Enum):
            return obj.value
        
        if isinstance(obj, bytes):
            import base64
            return base64.b64encode(obj).decode('utf-8')
        
        if isinstance(obj, set):
            return list(obj)
        
        return super().default(obj)


class JSONExporter(BaseExporter):
    """
    Exportador de datos a formato JSON.
    
    Genera un documento JSON con:
        - Metadatos (fecha, filtros, total)
        - Array de datos
        - Resumen estadístico (opcional)
    
    Estructura del JSON:
        {
            "metadatos": {
                "fecha_exportacion": "2025-01-30T12:00:00",
                "formato": "json",
                "total_registros": 100,
                "filtros": {...}
            },
            "datos": [
                {...},
                {...}
            ],
            "resumen": {...}  // opcional
        }
    
    Ejemplo:
        exporter = JSONExporter(nombre_archivo="sesiones")
        json_bytes = exporter.exportar(datos)
    """
    
    def __init__(
        self,
        nombre_archivo: str = "exportacion",
        filtros: FiltroExportacion = None,
        pretty: bool = True,
        incluir_metadatos: bool = True,
        incluir_resumen: bool = False
    ):
        """
        Inicializa el exportador JSON.
        
        Args:
            nombre_archivo: Nombre base del archivo
            filtros: Filtros de exportación
            pretty: Si formatear con indentación
            incluir_metadatos: Si incluir sección de metadatos
            incluir_resumen: Si calcular e incluir resumen
        """
        super().__init__(nombre_archivo, filtros)
        self.pretty = pretty
        self.incluir_metadatos = incluir_metadatos
        self.incluir_resumen = incluir_resumen
        self._datos = []
        self._campos = []
    
    # --- Implementación de métodos abstractos ---
    
    def get_formato(self) -> FormatoExportacion:
        return FormatoExportacion.JSON
    
    def get_extension(self) -> str:
        return "json"
    
    def get_content_type(self) -> str:
        return "application/json; charset=utf-8"
    
    def _inicializar_buffer(self) -> None:
        """Inicializa la lista de datos."""
        self._datos = []
    
    def _escribir_encabezados(self, campos: List[str]) -> None:
        """Guarda los campos para el resumen."""
        self._campos = campos
    
    def _escribir_fila(self, datos: Dict[str, Any]) -> None:
        """Añade los datos a la lista."""
        self._datos.append(datos)
    
    def _finalizar(self) -> bytes:
        """Genera el JSON final con metadatos."""
        # Construir documento
        documento = {}
        
        # Metadatos
        if self.incluir_metadatos:
            self.metadatos['total_registros'] = len(self._datos)
            documento['metadatos'] = self.metadatos
        
        # Datos
        documento['datos'] = self._datos
        
        # Resumen (opcional)
        if self.incluir_resumen and self._datos:
            documento['resumen'] = self._generar_resumen()
        
        # Serializar
        indent = 2 if self.pretty else None
        
        json_str = json.dumps(
            documento,
            cls=JSONEncoder,
            ensure_ascii=False,
            indent=indent
        )
        
        return json_str.encode('utf-8')
    
    # --- Métodos auxiliares ---
    
    def _generar_resumen(self) -> Dict[str, Any]:
        """
        Genera un resumen estadístico de los datos.
        
        Calcula:
            - Total de registros
            - Campos numéricos: min, max, promedio
            - Campos de fecha: primera y última
        """
        resumen = {
            'total': len(self._datos)
        }
        
        if not self._datos:
            return resumen
        
        # Analizar cada campo
        for campo in self._campos:
            valores = [d.get(campo) for d in self._datos if d.get(campo) is not None]
            
            if not valores:
                continue
            
            # Detectar tipo
            primer_valor = valores[0]
            
            if isinstance(primer_valor, (int, float)):
                # Campo numérico
                resumen[f'{campo}_stats'] = {
                    'min': min(valores),
                    'max': max(valores),
                    'promedio': sum(valores) / len(valores),
                    'total': sum(valores)
                }
            
            elif isinstance(primer_valor, str):
                # Intentar detectar fechas
                if 'T' in primer_valor or '-' in primer_valor:
                    try:
                        fechas = sorted(valores)
                        resumen[f'{campo}_rango'] = {
                            'primera': fechas[0],
                            'ultima': fechas[-1]
                        }
                    except:
                        pass
                else:
                    # Contar valores únicos
                    unicos = set(valores)
                    if len(unicos) <= 10:
                        conteo = {v: valores.count(v) for v in unicos}
                        resumen[f'{campo}_distribucion'] = conteo
        
        return resumen
    
    def exportar_solo_datos(self, datos: List[Dict[str, Any]]) -> bytes:
        """
        Exporta solo el array de datos sin metadatos.
        
        Útil para APIs que solo necesitan los datos.
        """
        json_str = json.dumps(
            datos,
            cls=JSONEncoder,
            ensure_ascii=False,
            indent=2 if self.pretty else None
        )
        
        return json_str.encode('utf-8')


# Registrar el exportador en la Factory
ExporterFactory.registrar(FormatoExportacion.JSON, JSONExporter)
