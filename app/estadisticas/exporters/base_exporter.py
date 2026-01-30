# ==============================================================================
# 📊 EXPORTADOR BASE - Factory Pattern + Polimorfismo
# ==============================================================================
#
# Implementación del patrón Factory para exportación de datos.
# Cada formato (CSV, JSON, Excel) tiene su propia clase que hereda de BaseExporter.
#
# Patrones implementados:
#   - Factory Method: ExporterFactory crea el exportador correcto
#   - Template Method: BaseExporter define el algoritmo, subclases implementan pasos
#   - Strategy: Cada exportador es una estrategia diferente
#
# ==============================================================================

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Type
from enum import Enum
import io
import os


class FormatoExportacion(Enum):
    """Formatos de exportación disponibles."""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PDF = "pdf"


class FiltroExportacion:
    """
    Clase para encapsular filtros de exportación.
    
    Permite filtrar datos por:
        - Rango de fechas
        - Usuario específico
        - Parada específica
        - Tipo de actividad
        - Estado
    
    Ejemplo:
        filtro = FiltroExportacion(
            fecha_inicio=datetime(2025, 1, 1),
            fecha_fin=datetime(2025, 12, 31),
            usuario_id=5
        )
    """
    
    def __init__(
        self,
        fecha_inicio: datetime = None,
        fecha_fin: datetime = None,
        usuario_id: int = None,
        parada_id: int = None,
        tipo_actividad: str = None,
        estado: str = None,
        limite: int = None,
        orden: str = 'desc'
    ):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.usuario_id = usuario_id
        self.parada_id = parada_id
        self.tipo_actividad = tipo_actividad
        self.estado = estado
        self.limite = limite
        self.orden = orden
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte los filtros a diccionario (para logs)."""
        return {
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'usuario_id': self.usuario_id,
            'parada_id': self.parada_id,
            'tipo_actividad': self.tipo_actividad,
            'estado': self.estado,
            'limite': self.limite,
            'orden': self.orden
        }
    
    def aplicar_a_query(self, query, modelo):
        """
        Aplica los filtros a una query SQLAlchemy.
        
        Args:
            query: Query base de SQLAlchemy
            modelo: Clase del modelo para acceder a sus campos
            
        Returns:
            Query con filtros aplicados
        """
        if self.fecha_inicio and hasattr(modelo, 'fecha_creacion'):
            query = query.filter(modelo.fecha_creacion >= self.fecha_inicio)
        
        if self.fecha_fin and hasattr(modelo, 'fecha_creacion'):
            query = query.filter(modelo.fecha_creacion <= self.fecha_fin)
        
        if self.usuario_id and hasattr(modelo, 'usuario_id'):
            query = query.filter(modelo.usuario_id == self.usuario_id)
        
        if self.parada_id and hasattr(modelo, 'parada_id'):
            query = query.filter(modelo.parada_id == self.parada_id)
        
        if self.tipo_actividad and hasattr(modelo, 'tipo_actividad'):
            query = query.filter(modelo.tipo_actividad == self.tipo_actividad)
        
        if self.estado and hasattr(modelo, 'estado'):
            query = query.filter(modelo.estado == self.estado)
        
        # Ordenamiento
        if hasattr(modelo, 'fecha_creacion'):
            if self.orden == 'asc':
                query = query.order_by(modelo.fecha_creacion.asc())
            else:
                query = query.order_by(modelo.fecha_creacion.desc())
        
        # Límite
        if self.limite:
            query = query.limit(self.limite)
        
        return query


class BaseExporter(ABC):
    """
    Clase base abstracta para exportadores.
    
    Implementa el patrón Template Method:
        - exportar() define el algoritmo general
        - Las subclases implementan los pasos específicos
    
    Atributos:
        - formato: Formato de exportación
        - nombre_archivo: Nombre base del archivo
        - filtros: Filtros aplicados
        - metadatos: Info adicional sobre la exportación
    
    Métodos abstractos (deben implementar las subclases):
        - _escribir_encabezados()
        - _escribir_fila()
        - _finalizar()
        - get_extension()
        - get_content_type()
    """
    
    def __init__(
        self,
        nombre_archivo: str = "exportacion",
        filtros: FiltroExportacion = None
    ):
        self.nombre_archivo = nombre_archivo
        self.filtros = filtros or FiltroExportacion()
        self.metadatos = {
            'fecha_exportacion': datetime.utcnow().isoformat(),
            'formato': self.get_formato().value,
            'filtros': self.filtros.to_dict()
        }
        self._buffer = None
        self._datos_exportados = 0
    
    # --- Métodos abstractos (Template Method) ---
    
    @abstractmethod
    def get_formato(self) -> FormatoExportacion:
        """Devuelve el formato de exportación."""
        pass
    
    @abstractmethod
    def get_extension(self) -> str:
        """Devuelve la extensión del archivo (sin punto)."""
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Devuelve el Content-Type para HTTP."""
        pass
    
    @abstractmethod
    def _inicializar_buffer(self) -> None:
        """Inicializa el buffer de escritura."""
        pass
    
    @abstractmethod
    def _escribir_encabezados(self, campos: List[str]) -> None:
        """Escribe los encabezados/cabecera."""
        pass
    
    @abstractmethod
    def _escribir_fila(self, datos: Dict[str, Any]) -> None:
        """Escribe una fila de datos."""
        pass
    
    @abstractmethod
    def _finalizar(self) -> bytes:
        """Finaliza y devuelve los bytes del archivo."""
        pass
    
    # --- Template Method principal ---
    
    def exportar(
        self,
        datos: List[Dict[str, Any]],
        campos: List[str] = None
    ) -> bytes:
        """
        Método principal de exportación (Template Method).
        
        Define el algoritmo general:
            1. Inicializar buffer
            2. Escribir encabezados
            3. Escribir cada fila
            4. Finalizar y devolver bytes
        
        Args:
            datos: Lista de diccionarios con los datos
            campos: Lista de campos a incluir (None = todos)
            
        Returns:
            Bytes del archivo generado
        """
        if not datos:
            datos = []
        
        # Determinar campos si no se especifican
        if not campos and datos:
            campos = list(datos[0].keys())
        elif not campos:
            campos = []
        
        # 1. Inicializar
        self._inicializar_buffer()
        
        # 2. Encabezados
        self._escribir_encabezados(campos)
        
        # 3. Datos
        for fila in datos:
            # Filtrar solo los campos solicitados
            fila_filtrada = {k: fila.get(k) for k in campos}
            self._escribir_fila(fila_filtrada)
            self._datos_exportados += 1
        
        # 4. Finalizar
        return self._finalizar()
    
    def exportar_modelo(
        self,
        modelo_clase,
        campos: List[str] = None,
        include_relations: bool = False
    ) -> bytes:
        """
        Exporta directamente desde un modelo SQLAlchemy.
        
        Args:
            modelo_clase: Clase del modelo (ej: Sesion)
            campos: Campos a incluir
            include_relations: Si incluir relaciones
            
        Returns:
            Bytes del archivo generado
        """
        # Obtener query base
        query = modelo_clase.query
        
        # Aplicar filtros
        query = self.filtros.aplicar_a_query(query, modelo_clase)
        
        # Obtener datos
        registros = query.all()
        
        # Convertir a diccionarios
        datos = [
            r.to_dict(include_relations=include_relations) 
            for r in registros
        ]
        
        # Actualizar metadatos
        self.metadatos['modelo'] = modelo_clase.__name__
        self.metadatos['total_registros'] = len(datos)
        
        return self.exportar(datos, campos)
    
    def get_nombre_archivo_completo(self) -> str:
        """Genera nombre de archivo con timestamp."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{self.nombre_archivo}_{timestamp}.{self.get_extension()}"
    
    def guardar_archivo(self, directorio: str = ".") -> str:
        """
        Guarda el archivo en disco.
        
        Args:
            directorio: Directorio destino
            
        Returns:
            Ruta completa del archivo guardado
        """
        if self._buffer is None:
            raise ValueError("No hay datos exportados. Llama a exportar() primero.")
        
        ruta = os.path.join(directorio, self.get_nombre_archivo_completo())
        
        with open(ruta, 'wb') as f:
            contenido = self._finalizar()
            f.write(contenido)
        
        return ruta


class ExporterFactory:
    """
    Factory para crear exportadores.
    
    Implementa el patrón Factory Method, centralizando
    la creación de exportadores.
    
    Ejemplo:
        # Crear exportador CSV
        exporter = ExporterFactory.crear(FormatoExportacion.CSV)
        
        # O usando string
        exporter = ExporterFactory.crear_desde_string("json")
    """
    
    # Registro de exportadores disponibles
    _exportadores: Dict[FormatoExportacion, Type[BaseExporter]] = {}
    
    @classmethod
    def registrar(
        cls,
        formato: FormatoExportacion,
        exporter_clase: Type[BaseExporter]
    ):
        """
        Registra un nuevo tipo de exportador.
        
        Args:
            formato: Formato que maneja
            exporter_clase: Clase del exportador
        """
        cls._exportadores[formato] = exporter_clase
    
    @classmethod
    def crear(
        cls,
        formato: FormatoExportacion,
        nombre_archivo: str = "exportacion",
        filtros: FiltroExportacion = None
    ) -> BaseExporter:
        """
        Crea un exportador del formato especificado.
        
        Args:
            formato: Formato de exportación
            nombre_archivo: Nombre base del archivo
            filtros: Filtros a aplicar
            
        Returns:
            Instancia del exportador
            
        Raises:
            ValueError: Si el formato no está soportado
        """
        if formato not in cls._exportadores:
            raise ValueError(
                f"Formato '{formato.value}' no soportado. "
                f"Disponibles: {[f.value for f in cls._exportadores.keys()]}"
            )
        
        exporter_clase = cls._exportadores[formato]
        return exporter_clase(nombre_archivo, filtros)
    
    @classmethod
    def crear_desde_string(
        cls,
        formato_str: str,
        nombre_archivo: str = "exportacion",
        filtros: FiltroExportacion = None
    ) -> BaseExporter:
        """
        Crea exportador a partir de string.
        
        Args:
            formato_str: "csv", "json", "excel"
        """
        try:
            formato = FormatoExportacion(formato_str.lower())
            return cls.crear(formato, nombre_archivo, filtros)
        except ValueError:
            formatos_validos = [f.value for f in FormatoExportacion]
            raise ValueError(
                f"Formato '{formato_str}' no válido. "
                f"Usa uno de: {formatos_validos}"
            )
    
    @classmethod
    def get_formatos_disponibles(cls) -> List[str]:
        """Lista los formatos disponibles."""
        return [f.value for f in cls._exportadores.keys()]
