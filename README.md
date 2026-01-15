# 🚢 MentxuApp Backend

Backend web y API REST para **MentxuApp**, una aplicación de recorrido turístico interactivo por Santurtzi con mini-juegos educativos.

## 📋 Descripción

Este proyecto proporciona:
- **Panel de administración web** para visualizar estadísticas y gestionar usuarios
- **API REST** para la sincronización de datos con la app móvil Android
- **Base de datos** para almacenar usuarios, paradas y progreso
- **Interfaz visual** con mapa interactivo de Google Maps

## 🎯 Características

### Panel Web
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Mapa interactivo con las 6 paradas de Santurtzi
- ✅ Gestión de usuarios y visualización de progreso
- ✅ Panel de administración
- ✅ Gráficos con Chart.js
- ✅ Diseño responsive con temática marítima

### API REST
- ✅ CRUD de paradas
- ✅ Registro de usuarios desde app móvil
- ✅ Gestión de progreso (completar paradas, estadísticas)
- ✅ Endpoints de estadísticas generales
- ✅ CORS habilitado para app Android

## 🛠️ Tecnologías

- **Python 3.8+**
- **Flask 3.0** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos (desarrollo)
- **Bootstrap 5** - Framework CSS
- **Chart.js** - Gráficos interactivos
- **Google Maps API** - Mapa interactivo

## 📦 Instalación

### 1. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `.env.example` a `.env` y configura:

```bash
cp .env.example .env
```

Edita `.env`:
```env
SECRET_KEY=tu-clave-secreta-super-segura
GOOGLE_MAPS_API_KEY=tu-api-key-de-google-maps
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 4. Inicializar base de datos

```bash
python init_db.py
```

Esto creará:
- Usuario admin por defecto (`admin` / `admin123`)
- Las 6 paradas de Santurtzi con datos completos

### 5. Ejecutar el servidor

```bash
python run.py
```

El servidor estará disponible en:
- **Web**: http://localhost:5000
- **Dashboard**: http://localhost:5000/dashboard
- **API**: http://localhost:5000/api/paradas

## 🗺️ Paradas del Recorrido

1. **Ayuntamiento (Mentxu)** - Sopa de letras
2. **Escultura "El niño y el perro"** - Encuentra las diferencias
3. **Barco Agurtza** - Juego de relacionar
4. **Museo Marítimo** - Recogida de basura
5. **Puerto** - Proceso de pesca
6. **Monumento Niños de la Guerra** - Puzzle

## 📡 API REST Endpoints

### Paradas
```
GET    /api/paradas              # Listar todas las paradas
GET    /api/paradas/<id>         # Obtener una parada
GET    /api/paradas/<id>/estadisticas  # Estadísticas de parada
POST   /api/paradas              # Crear parada (requiere auth)
PUT    /api/paradas/<id>         # Actualizar parada (requiere auth)
DELETE /api/paradas/<id>         # Eliminar parada (requiere auth)
```

### Usuarios
```
GET    /api/usuarios             # Listar usuarios
GET    /api/usuarios/<id>        # Obtener un usuario
POST   /api/usuarios/registro    # Registrar nuevo usuario
GET    /api/usuarios/<id>/progreso  # Progreso de usuario
DELETE /api/usuarios/<id>        # Eliminar usuario (admin)
```

### Progreso
```
GET    /api/progreso/<usuario_id>    # Progreso completo
POST   /api/progreso/completar       # Marcar parada completada
PUT    /api/progreso/<id>            # Actualizar progreso
GET    /api/estadisticas             # Estadísticas generales
```

## 🔐 Autenticación

El panel web requiere autenticación:
- **Usuario por defecto**: `admin`
- **Contraseña por defecto**: `admin123`

La API REST es pública para lectura, pero requiere autenticación para escritura.

## 📱 Integración con App Android

### Ejemplo: Registrar usuario desde Android

```kotlin
// En tu app Android
val retrofit = Retrofit.Builder()
    .baseUrl("http://tu-servidor:5000/api/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

// Registro
val request = RegistroRequest(
    nombre = "Juan",
    apellido = "García",
    device_id = "unique-device-id"
)
api.registrarUsuario(request)
```

### Ejemplo: Completar parada

```kotlin
val progreso = CompletarParadaRequest(
    usuario_id = 1,
    parada_id = 2,
    puntuacion = 85,
    tiempo_empleado = 120  // segundos
)
api.completarParada(progreso)
```

## 📁 Estructura del Proyecto

```
MentxuBackend/
├── app/
│   ├── __init__.py          # Factory de la aplicación
│   ├── models.py            # Modelos de datos
│   ├── routes/
│   │   ├── auth.py          # Rutas de autenticación
│   │   ├── web.py           # Rutas web (páginas HTML)
│   │   ├── paradas.py       # API de paradas
│   │   ├── usuarios.py      # API de usuarios
│   │   └── progreso.py      # API de progreso
│   ├── static/
│   │   └── css/style.css    # Estilos personalizados
│   └── templates/           # Templates HTML
├── instance/
│   └── mentxuapp.db         # Base de datos SQLite
├── config.py                # Configuración
├── run.py                   # Punto de entrada
├── init_db.py              # Inicializar BD
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## 🎨 Capturas de Pantalla

### Dashboard
Panel principal con estadísticas, gráficos y usuarios recientes.

### Mapa Interactivo
Visualización de las 6 paradas en Google Maps con marcadores numerados.

### Gestión de Usuarios
Lista completa de usuarios con su progreso individual.

## 🚀 Despliegue en Producción

### Heroku

```bash
# Instalar Heroku CLI
heroku create mentxuapp-backend

# Añadir PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurar variables de entorno
heroku config:set SECRET_KEY=tu-clave-secreta
heroku config:set GOOGLE_MAPS_API_KEY=tu-api-key

# Deploy
git push heroku main

# Inicializar BD
heroku run python init_db.py
```

### Railway / Render

Similar a Heroku, ambos soportan aplicaciones Flask automáticamente.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Añadir funcionalidad X'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto forma parte de **MentxuApp** - Recorrido turístico por Santurtzi.

## 👥 Autores

- **Gaizka Rodriguez**
- **Xiker García**
- **Diego Fernandez**

---

**MentxuApp** - Descubre Santurtzi 🌊⚓
