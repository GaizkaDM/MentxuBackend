# ==============================================================================
# 📊 EXPORTADOR CSV - Exportación a CSV con filtros
# ==============================================================================
#
# Exporta datos a formato CSV usando el módulo nativo de Python.
# Soporta:
#   - Campos personalizados
#   - Filtros de fecha, usuario, etc.
#   - Codificación UTF-8 con BOM (para Excel)
#
# ==============================================================================

import csv
import io
from typing import Dict, List, Any
from .base_exporter import (
    BaseExporter, 
    ExporterFactory, 
    FormatoExportacion,
    FiltroExportacion
)


class CSVExporter(BaseExporter):
    """
    Exportador de datos a formato CSV.
    
    Hereda de BaseExporter e implementa los métodos abstractos
    para generar archivos CSV.
    
    Características:
        - UTF-8 con BOM para compatibilidad con Excel
        - Delimitador configurable (por defecto coma)
        - Escape automático de caracteres especiales
    
    Ejemplo:
        exporter = CSVExporter(nombre_archivo="usuarios")
        datos = [
            {"id": 1, "nombre": "Juan"},
            {"id": 2, "nombre": "María"}
        ]
        csv_bytes = exporter.exportar(datos)
    """
    
    def __init__(
        self,
        nombre_archivo: str = "exportacion",
        filtros: FiltroExportacion = None,
        delimitador: str = ",",
        incluir_bom: bool = True
    ):
        """
        Inicializa el exportador CSV.
        
        Args:
            nombre_archivo: Nombre base del archivo
            filtros: Filtros de exportación
            delimitador: Separador de campos (coma, punto y coma, tab)
            incluir_bom: Si incluir BOM para Excel
        """
        super().__init__(nombre_archivo, filtros)
        self.delimitador = delimitador
        self.incluir_bom = incluir_bom
        self._writer = None
        self._campos = []
    
    # --- Implementación de métodos abstractos ---
    
    def get_formato(self) -> FormatoExportacion:
        return FormatoExportacion.CSV
    
    def get_extension(self) -> str:
        return "csv"
    
    def get_content_type(self) -> str:
        return "text/csv; charset=utf-8"
    
    def _inicializar_buffer(self) -> None:
        """Crea el buffer de escritura CSV."""
        self._buffer = io.StringIO()
        
        # BOM para Excel (UTF-8)
        if self.incluir_bom:
            self._buffer.write('\ufeff')
        
        self._writer = csv.writer(
            self._buffer,
            delimiter=self.delimitador,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator='\n'
        )
    
    def _escribir_encabezados(self, campos: List[str]) -> None:
        """Escribe la fila de encabezados."""
        self._campos = campos
        
        # Convertir campos a legibles
        encabezados = [self._formatear_encabezado(c) for c in campos]
        self._writer.writerow(encabezados)
    
    def _escribir_fila(self, datos: Dict[str, Any]) -> None:
        """Escribe una fila de datos."""
        fila = []
        
        for campo in self._campos:
            valor = datos.get(campo, "")
            fila.append(self._formatear_valor(valor))
        
        self._writer.writerow(fila)
    
    def _finalizar(self) -> bytes:
        """Devuelve el contenido como bytes."""
        contenido = self._buffer.getvalue()
        return contenido.encode('utf-8')
    
    # --- Métodos auxiliares ---
    
    def _formatear_encabezado(self, campo: str) -> str:
        """
        Convierte nombre de campo a encabezado legible.
        
        Ejemplos:
            - "fecha_creacion" → "Fecha Creación"
            - "usuario_id" → "Usuario ID"
        """
        # Reemplazar guiones bajos por espacios
        palabras = campo.replace('_', ' ').split()
        
        # Capitalizar cada palabra
        return ' '.join(p.title() for p in palabras)
    
    def _formatear_valor(self, valor: Any) -> str:
        """
        Convierte un valor a string para CSV.
        
        Maneja:
            - None → cadena vacía
            - Listas → separadas por |
            - Diccionarios → JSON inline
            - Booleanos → Sí/No
        """
        if valor is None:
            return ""
        
        if isinstance(valor, bool):
            return "Sí" if valor else "No"
        
        if isinstance(valor, list):
            return " | ".join(str(v) for v in valor)
        
        if isinstance(valor, dict):
            import json
            return json.dumps(valor, ensure_ascii=False)
        
        return str(valor)


# Registrar el exportador en la Factory
ExporterFactory.registrar(FormatoExportacion.CSV, CSVExporter)
