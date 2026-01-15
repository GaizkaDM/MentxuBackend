# 🚀 Guía Rápida de Inicio - MentxuApp Backend

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Crear entorno virtual

```bash
python -m venv venv
```

### 2️⃣ Activar entorno virtual

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Inicializar base de datos

```bash
python init_db.py
```

**Esto creará:**
- ✅ Base de datos SQLite
- ✅ Usuario admin (admin / admin123)
- ✅ 6 paradas de Santurtzi

### 5️⃣ Ejecutar servidor

```bash
python run.py
```

### 6️⃣ Abrir en el navegador

- **Página principal:** http://localhost:5000
- **Login:** http://localhost:5000/login
- **Dashboard:** http://localhost:5000/dashboard (requiere login)

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🌐 URLs Disponibles

### Páginas Web (Interfaz)
```
http://localhost:5000/              # Landing page
http://localhost:5000/login         # Login
http://localhost:5000/dashboard     # Dashboard (auth requerida)
http://localhost:5000/mapa          # Mapa interactivo (auth requerida)
http://localhost:5000/usuarios      # Lista de usuarios (auth requerida)
http://localhost:5000/admin         # Panel admin (auth requerida)
```

### API REST (Endpoints)
```
http://localhost:5000/api/paradas               # GET - Listar paradas
http://localhost:5000/api/paradas/1             # GET - Ver parada #1
http://localhost:5000/api/usuarios              # GET - Listar usuarios
http://localhost:5000/api/usuarios/registro     # POST - Registrar usuario
http://localhost:5000/api/progreso/1            # GET - Progreso usuario #1
http://localhost:5000/api/progreso/completar    # POST - Completar parada
http://localhost:5000/api/estadisticas          # GET - Estadísticas
```

---

## 🧪 Probar la API

### Con cURL (Windows PowerShell)

**Obtener todas las paradas:**
```powershell
curl http://localhost:5000/api/paradas
```

**Registrar un usuario:**
```powershell
curl -X POST http://localhost:5000/api/usuarios/registro `
  -H "Content-Type: application/json" `
  -d '{"nombre":"Juan","apellido":"Pérez","device_id":"test-device-123"}'
```

**Completar una parada:**
```powershell
curl -X POST http://localhost:5000/api/progreso/completar `
  -H "Content-Type: application/json" `
  -d '{"usuario_id":1,"parada_id":1,"puntuacion":100,"tiempo_empleado":60}'
```

### Con Postman / Insomnia

Importa esta colección base:

**GET** http://localhost:5000/api/paradas
**GET** http://localhost:5000/api/estadisticas
**POST** http://localhost:5000/api/usuarios/registro
```json
{
  "nombre": "María",
  "apellido": "García",
  "device_id": "android-test-001"
}
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
# Asegúrate de tener el entorno virtual activado
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Address already in use"
El puerto 5000 ya está ocupado. Cambia el puerto en `run.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### No aparece Google Maps
Configura tu API Key en `.env`:
```
GOOGLE_MAPS_API_KEY=tu-api-key-aqui
```

### No puedo hacer login
Verifica que inicializaste la BD:
```bash
python init_db.py
```

---

## 📱 Conectar con App Android

En tu app Android, cambia la URL base:

```kotlin
// En desarrollo (emulador)
const val BASE_URL = "http://10.0.2.2:5000/api/"

// En dispositivo físico (misma red WiFi)
const val BASE_URL = "http://TU-IP-LOCAL:5000/api/"
```

Para saber tu IP local:
```bash
ipconfig    # Windows
ifconfig    # Linux/Mac
```

---

## 📊 Datos de Prueba

Después de inicializar, tendrás:
- **1 admin:** admin / admin123
- **6 paradas:** Ayuntamiento, Escultura, Barco, Museo, Puerto, Monumento
- **0 usuarios:** (se crean al registrarse desde la app)

---

## 🛑 Detener el Servidor

Presiona `CTRL + C` en la terminal donde está corriendo.

---

## ✅ Checklist de Configuración

- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos inicializada (`python init_db.py`)
- [ ] Archivo `.env` configurado (opcional)
- [ ] Servidor funcionando (`python run.py`)
- [ ] Dashboard accesible con login admin
- [ ] API REST respondiendo en `/api/paradas`

---

## 📧 Soporte

Si tienes problemas, verifica:
1. Python 3.8+ instalado
2. pip actualizado (`python -m pip install --upgrade pip`)
3. Entorno virtual activado
4. Todos los archivos del proyecto presentes

---

**¡Listo para usar! 🎉**
