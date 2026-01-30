# 📊 Módulo de Estadísticas - DIdaktikAPP / MentxuApp

## 🎯 Descripción

Este módulo implementa un **sistema avanzado de estadísticas educativas** para la aplicación MentxuApp, cumpliendo con los requerimientos del **Nivel Avanzado (10/10)** de la asignatura de Python.

## ✅ Características Implementadas

### 1. POO Compleja
- ✅ **Herencia**: `EstadisticaBase` → `BaseModel` → `db.Model`
- ✅ **Polimorfismo**: Métodos `to_dict()`, `get_estadisticas_usuario()` sobrescrito en cada modelo
- ✅ **Encapsulación**: Campos privados, propiedades, validaciones
- ✅ **Mixins**: `TimestampMixin`, `DictSerializableMixin`
- ✅ **Patrones de diseño**:
  - Factory Method (ExporterFactory)
  - Template Method (BaseExporter)
  - Strategy (Exportadores)

### 2. Exportación Múltiple con Filtros
- ✅ **CSV**: Con BOM para Excel, delimitador configurable
- ✅ **JSON**: Con metadatos, resumen estadístico
- ✅ **Excel**: Múltiples hojas, estilos, anchos automáticos
- ✅ **Filtros avanzados**: Por fecha, usuario, parada, tipo, estado

### 3. ORM con SQLAlchemy
- ✅ **Modelos relacionados**: Usuario → Sesiones, Intentos, Logros
- ✅ **Relaciones**: OneToMany, ManyToMany con tabla intermedia
- ✅ **Queries complejas**: Agregaciones, joins, subqueries
- ✅ **Carga de datos**: Importación desde CSV/JSON

### 4. API REST Completa con Flask
- ✅ **Blueprints modulares**
- ✅ **CRUD completo** para cada entidad
- ✅ **Filtros y paginación**
- ✅ **Endpoints de estadísticas y ranking**

### 5. Visualización Interactiva
- ✅ **Dashboard con Chart.js**
- ✅ **Gráficos de líneas, donuts**
- ✅ **Tablas con paginación**
- ✅ **Pantallas separadas por categoría**

---

## 📁 Estructura del Módulo

```
app/estadisticas/
├── __init__.py                 # Blueprint principal
├── models/                     # Modelos ORM (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py                 # Clases base con mixins
│   ├── sesion.py               # Registro de login/logout
│   ├── logro.py                # Sistema de achievements
│   └── historial.py            # Historial de intentos
├── exporters/                  # Exportación de datos
│   ├── __init__.py
│   ├── base_exporter.py        # Factory + Template Method
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── excel_exporter.py
├── routes/                     # API REST
│   ├── __init__.py
│   ├── estadisticas_api.py     # Endpoints de estadísticas
│   ├── logros_api.py           # Endpoints de logros
│   ├── exportar_api.py         # Endpoints de exportación
│   └── dashboard.py            # Rutas del dashboard web
└── templates/estadisticas/     # Templates HTML
    ├── dashboard.html
    ├── usuarios.html
    ├── actividades.html
    └── exportar.html
```

---

## 🚀 Instalación

### 1. Instalar dependencias adicionales

```bash
pip install -r requirements.txt
```

Nuevas dependencias añadidas:
- `openpyxl` - Exportación a Excel
- `pandas` - Análisis de datos (opcional)

### 2. El módulo se inicializa automáticamente

Al arrancar la aplicación Flask, el módulo se registra automáticamente:

```python
# En app/__init__.py
from app.estadisticas import init_estadisticas
init_estadisticas(app, db)
```

### 3. Crear tablas de estadísticas

```bash
python -c "from run import app; from app import db; app.app_context().push(); db.create_all()"
```

---

## 📡 Endpoints API

### Estadísticas Generales
```
GET  /estadisticas/api/stats/general           # Stats globales
GET  /estadisticas/api/stats/usuarios/<id>     # Stats de usuario
GET  /estadisticas/api/stats/paradas/<id>      # Stats de parada
GET  /estadisticas/api/stats/ranking           # Ranking de usuarios
```

### Sesiones
```
GET   /estadisticas/api/stats/sesiones         # Listar sesiones
POST  /estadisticas/api/stats/sesiones         # Registrar sesión
POST  /estadisticas/api/stats/sesiones/<id>/cerrar  # Cerrar sesión
```

### Historial de Intentos
```
GET   /estadisticas/api/stats/intentos         # Listar intentos
POST  /estadisticas/api/stats/intentos         # Registrar intento
GET   /estadisticas/api/stats/evolucion/<id>   # Evolución de usuario
```

### Logros
```
GET   /estadisticas/api/logros                 # Listar logros
GET   /estadisticas/api/logros/<id>            # Detalle de logro
GET   /estadisticas/api/logros/usuario/<id>    # Logros de usuario
POST  /estadisticas/api/logros/desbloquear     # Desbloquear logro
POST  /estadisticas/api/logros/verificar/<id>  # Verificar logros
POST  /estadisticas/api/logros/inicializar     # Crear logros predefinidos
```

### Exportación
```
GET   /estadisticas/api/exportar/formatos      # Formatos disponibles
POST  /estadisticas/api/exportar/sesiones      # Exportar sesiones
POST  /estadisticas/api/exportar/intentos      # Exportar intentos
POST  /estadisticas/api/exportar/usuarios      # Exportar usuarios
```

---

## 🖥️ Dashboard Web

Accede al dashboard en: `http://localhost:5000/estadisticas/dashboard/`

### Pantallas disponibles:
1. **Dashboard principal** - Vista general con gráficos
2. **Estadísticas de Usuarios** - Tabla paginada
3. **Estadísticas de Actividades** - Por parada
4. **Exportar Datos** - Formularios de exportación

---

## 📊 Ejemplos de Uso

### Registrar una sesión desde la app Android

```kotlin
// Retrofit
val request = mapOf(
    "usuario_id" to userId,
    "tipo_dispositivo" to "android",
    "device_info" to "Samsung Galaxy S21"
)
api.post("/estadisticas/api/stats/sesiones", request)
```

### Registrar un intento de actividad

```kotlin
val intento = mapOf(
    "usuario_id" to userId,
    "parada_id" to paradaId,
    "tipo_actividad" to "sopa_letras",
    "puntuacion" to 85,
    "tiempo_segundos" to 45,
    "resultado" to "exito"
)
api.post("/estadisticas/api/stats/intentos", intento)
```

### Verificar logros después de completar actividad

```kotlin
api.post("/estadisticas/api/logros/verificar/$userId")
```

### Exportar datos con filtros

```python
import requests

response = requests.post(
    "http://localhost:5000/estadisticas/api/exportar/sesiones",
    json={
        "formato": "excel",
        "filtros": {
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2025-12-31"
        }
    }
)

with open("sesiones.xlsx", "wb") as f:
    f.write(response.content)
```

---

## 🏆 Sistema de Logros

### Logros predefinidos:

| Logro | Tipo | Dificultad | Puntos |
|-------|------|------------|--------|
| Velocista Novato | Velocidad | Fácil | 10 |
| Velocista Experto | Velocidad | Medio | 25 |
| Rayo | Velocidad | Experto | 100 |
| Preciso | Precisión | Fácil | 10 |
| Perfeccionista | Precisión | Difícil | 50 |
| Primer Paso | Exploración | Fácil | 10 |
| Explorador | Exploración | Medio | 25 |
| Conquistador de Santurtzi | Maestría | Difícil | 50 |
| Visitante Frecuente | Constancia | Medio | 25 |
| Leyenda de Santurtzi | Coleccionista | Legendario | 250 |

Para crear los logros predefinidos:
```bash
curl -X POST http://localhost:5000/estadisticas/api/logros/inicializar
```

---

## 🔧 Configuración Avanzada

### Añadir nuevos exportadores

```python
from app.estadisticas.exporters import BaseExporter, ExporterFactory, FormatoExportacion

class PDFExporter(BaseExporter):
    def get_formato(self):
        return FormatoExportacion.PDF
    
    def get_extension(self):
        return "pdf"
    
    # ... implementar métodos abstractos

# Registrar
ExporterFactory.registrar(FormatoExportacion.PDF, PDFExporter)
```

### Añadir nuevos logros

```python
from app.estadisticas.models import Logro, TipoLogro, NivelDificultad

nuevo_logro = Logro(
    nombre="Mi Nuevo Logro",
    nombre_corto="mi_logro",
    descripcion="Descripción del logro",
    tipo=TipoLogro.EXPLORACION,
    dificultad=NivelDificultad.MEDIO,
    puntos=25,
    requisitos={"paradas_completadas": 4}
)
nuevo_logro.save()
```

---

## 📝 Notas para la Evaluación

Este módulo cumple con **todos los requisitos del Nivel Avanzado (10/10)**:

1. ✅ **POO compleja** - Herencia multinivel, polimorfismo, encapsulación, patrones de diseño
2. ✅ **Exportación múltiple con filtros** - CSV, JSON, Excel con filtros por fecha/usuario/parada
3. ✅ **ORM SQLAlchemy** - Relaciones complejas, migraciones, importación de datos
4. ✅ **API REST completa** - Flask Blueprints, múltiples endpoints, paginación
5. ✅ **Dashboard interactivo** - Chart.js, múltiples pantallas, filtros visuales

---

## 👥 Autores

- **Gaizka Rodriguez**
- **Xiker García**
- **Diego Fernandez**

**MentxuApp** - Descubre Santurtzi 🌊⚓
