# 📊 Módulo de Estadísticas y Analytics - MentxuApp Backend

Este módulo implementa el sistema integral de **seguimiento, gamificación y análisis de datos** para la plataforma educativa MentxuApp. Proporciona herramientas para rastrear el progreso de los usuarios, gestionar logros y visualizar métricas clave a través de un dashboard interactivo.

## 🚀 Funcionalidades Principales

### 📈 Seguimiento y Analytics
*   **Registro de Sesiones**: Monitoreo de inicios de sesión, duración y dispositivos utilizados.
*   **Historial de Actividades**: Traza detallada de cada intento en los minijuegos (puntuación, tiempo, resultado).
*   **Progreso del Usuario**: Seguimiento del avance por las paradas y actividades del recorrido.

### 🏆 Gamificación (Sistema de Logros)
*   **Motor de Logros**: Sistema flexible para otorgar insignias basado en diferentes criterios (velocidad, precisión, exploración, constancia).
*   **Verificación Automática**: Evaluación de reglas en tiempo real al completar actividades.
*   **Tipos de Logros**:
    *   *Velocidad*: Completar tareas en tiempo récord.
    *   *Precisión*: Obtener puntuaciones perfectas.
    *   *Exploración*: Descubrir nuevas paradas.
    *   *Constancia*: Uso continuado de la aplicación.

### 💾 Exportación de Datos
Herramientas para extraer la información del sistema en formatos estándar para análisis externo:
*   **Formatos soportados**: CSV, JSON y Excel (.xlsx).
*   **Filtrado Avanzado**: Capacidad de filtrar exportaciones por rangos de fecha, tipos de usuario o actividades específicas.

### 🖥️ Dashboard de Administración
Interfaz web integrada en el backend para visualizar los datos:
*   **Gráficos Interactivos**: Visualización de tendencias, usuarios activos y tasas de completitud (usando Chart.js).
*   **Tablas de Datos**: Vistas detalladas de usuarios y actividades con paginación.
*   **Centro de Exportación**: Interfaz gráfica para generar y descargar informes.

---

## 🛠️ Arquitectura y Tecnologías

El módulo está construido siguiendo una arquitectura modular dentro de Flask:

*   **Lenguaje**: Python 3.x
*   **Framework Web**: Flask (organizado mediante `Blueprints`)
*   **ORM**: SQLAlchemy (con modelos relacionales complejos y mixins)
*   **Procesamiento de Datos**: Pandas & OpenPyXL (para generación de reportes)
*   **Frontend**: Jinja2 Templates + Bootstrap 5 + Chart.js

### Patrones de Diseño Aplicados
*   **Factory Method**: Para la instanciación de exportadores de datos.
*   **Template Method**: En la estructura base de los generadores de reportes.
*   **Strategy**: Para la implementación de diferentes reglas de logros.

---

## 📂 Estructura del Módulo

```
app/estadisticas/
├── models/               # Modelos de Base de Datos
│   ├── sesion.py         # Registro de accesos
│   ├── logro.py          # Definición y asignación de logros
│   └── historial.py      # Intentos y resultados de juegos
├── services/             # Lógica de Negocio
│   ├── estadisticas.py   # Cálculos y agregaciones
│   └── logros.py         # Motor de verificación de reglas
├── exporters/            # Motores de Exportación
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── excel_exporter.py
├── routes/               # API Endpoints
│   ├── api.py            # API REST para la app móvil
│   └── dashboard.py      # Controladores de la interfaz web
└── templates/            # Vistas HTML del Dashboard
```

---

## 🔌 API Reference

El módulo expone una API REST para la comunicación con la aplicación Android:

### Estadísticas
*   `POST /api/stats/sesiones`: Registrar inicio de sesión.
*   `POST /api/stats/intentos`: Registrar resultado de una actividad.
*   `GET /api/stats/usuario/<id>`: Obtener resumen de estadísticas de un usuario.

### Logros
*   `GET /api/logros`: Listar todos los logros disponibles.
*   `GET /api/logros/usuario/<id>`: Listar logros desbloqueados por un usuario.
*   `POST /api/logros/verificar/<id>`: Forzar verificación de logros (sync).

### Exportación
*   `POST /api/exportar/datos`: Endpoint para generar reportes programáticamente.

---

## ⚙️ Configuración e Instalación

Este módulo es parte del backend de MentxuApp y se inicializa automáticamente con la aplicación principal.

### Dependencias
Asegúrate de que `requirements.txt` incluya:
```txt
pandas>=1.3.0
openpyxl>=3.0.0
# ... otras dependencias base
```

### Inicialización de Datos
Para cargar los logros predefinidos en la base de datos (si es la primera vez que se despliega):

```bash
# Ejecutar script de inicialización o llamar al endpoint:
curl -X POST http://localhost:5000/estadisticas/api/logros/inicializar
```

---

## 👥 Autores y Mantenedores

*   **Gaizka Rodriguez**
*   **Xiker García**
*   **Diego Fernandez**

---
© 2025 MentxuApp Project - Todos los derechos reservados.
