# 🚀 Guía de Despliegue en Railway - MentxuApp Backend

## 📋 Preparación del Proyecto

### ✅ Archivos Necesarios (Ya Creados)

1. **Procfile** - Le dice a Railway cómo ejecutar la app
2. **runtime.txt** - Especifica versión de Python
3. **requirements.txt** - Con gunicorn añadido

---

## 🌐 Paso 1: Crear Cuenta en Railway

1. Ve a: **https://railway.app**
2. Click en **"Start a New Project"** o **"Login"**
3. Regístrate con:
   - GitHub (recomendado)
   - O con email

**Es GRATIS** - No necesitas tarjeta de crédito para empezar

---

## 📂 Paso 2: Subir Código a GitHub (Necesario)

Railway necesita que tu código esté en un repositorio Git.

### **Opción A: Crear repo nuevo en GitHub**

```powershell
# En el terminal, dentro de MentxuBackend
cd c:\Users\GaizkaClase\Desktop\MentxuBackend

# Si no has hecho git init (puede que ya lo hayas hecho)
git init

# Añadir todos los archivos
git add .

# Commit
git commit -m "Backend Flask listo para Railway"

# Crear repo en GitHub:
# 1. Ve a https://github.com/new
# 2. Nombre: MentxuApp-Backend
# 3. Público o Privado (tu eliges)
# 4. NO marques "Initialize with README"
# 5. Create repository

# Conectar con GitHub (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/MentxuApp-Backend.git
git branch -M main
git push -u origin main
```

---

## 🚂 Paso 3: Desplegar en Railway

### **3.1 Crear Nuevo Proyecto**

1. En Railway, click **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Autoriza Railway para acceder a GitHub
4. Selecciona el repositorio **"MentxuApp-Backend"**
5. Click en **"Deploy Now"**

### **3.2 Railway Detectará Automáticamente:**
- ✅ Que es una app Python
- ✅ Leerá `requirements.txt`
- ✅ Leerá `Procfile`
- ✅ Instalará dependencias
- ✅ Iniciará con Gunicorn

---

## ⚙️ Paso 4: Configurar Variables de Entorno

En Railway, ve a tu proyecto → **Variables** y añade:

```env
SECRET_KEY=tu-clave-super-secreta-de-produccion-cambiala-ahora
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/mentxuapp.db
```

**IMPORTANTE:** Cambia `SECRET_KEY` por algo único y seguro.

---

## 🗄️ Paso 5: Configurar Base de Datos (Opcional)

### **Opción A: Usar SQLite (más fácil)**
Ya está configurado en las variables de entorno arriba.

### **Opción B: Usar PostgreSQL (recomendado para producción)**

1. En Railway → **New** → **Database** → **PostgreSQL**
2. Railway creará automáticamente la variable `DATABASE_URL`
3. Actualiza `config.py` para usar PostgreSQL en producción

---

## 🔧 Paso 6: Inicializar Base de Datos

Railway ejecutará automáticamente tu app, pero necesitas inicializar la BD.

### **Opción 1: Usar Railway CLI (recomendado)**

```powershell
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Conectar al proyecto
railway link

# Ejecutar comando de inicialización
railway run python init_db.py
```

### **Opción 2: Modificar run.py para auto-inicializar**

Puedes hacer que se inicialice automáticamente al arrancar por primera vez.

---

## 🌍 Paso 7: Obtener tu URL

1. En Railway, ve a **Settings** → **Domains**
2. Click en **"Generate Domain"**
3. Railway te dará una URL como: `https://mentxuapp-backend-production.up.railway.app`

**Esta URL:**
- ✅ Tiene HTTPS automático
- ✅ Es gratis
- ✅ Está disponible 24/7

---

## 📱 Paso 8: Actualizar la App Android

En `build.gradle.kts`:

```kotlin
buildTypes {
    release {
        buildConfigField("String", "API_BASE_URL", 
            "\"https://tu-proyecto.up.railway.app/api/\"")
    }
}
```

Reemplaza con tu URL de Railway.

---

## ✅ Paso 9: Verificar que Funciona

1. Abre en navegador: `https://tu-proyecto.up.railway.app`
2. Deberías ver la landing page
3. Prueba: `https://tu-proyecto.up.railway.app/api/paradas`
4. Debería devolver JSON con las paradas

---

## 🔍 Debugging

### **Ver Logs en Railway:**
```
Railway Dashboard → Tu Proyecto → Deployments → View Logs
```

### **Errores Comunes:**

**1. "Application failed to respond"**
- Verifica que `Procfile` existe
- Verifica que `gunicorn` está en `requirements.txt`

**2. "Module not found"**
- Verifica que todas las dependencias están en `requirements.txt`
- Re-deploy

**3. "Database not found"**
- Ejecuta `railway run python init_db.py`

---

## 💰 Costos

Railway tiene un **plan gratuito** con:
- ✅ $5 USD de crédito gratis al mes
- ✅ Suficiente para apps pequeñas/medianas
- ✅ SSL/HTTPS incluido
- ✅ Sin tarjeta de crédito requerida

Si necesitas más, planes desde $5/mes.

---

## 🔐 Seguridad en Producción

### **Cosas a Cambiar:**

1. **SECRET_KEY** - Usa un generador:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **ADMIN_PASSWORD** - Cambia de `admin123` a algo seguro

3. **CORS Origin** - En `app/__init__.py`:
   ```python
   CORS(app, origins=[
       "https://tu-dominio.com",  # Solo tu app
       "http://localhost:5000"     # Solo para desarrollo
   ])
   ```

---

## 📊 Monitoreo

Railway te da:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Request logs
- ✅ Error tracking

Todo en el dashboard.

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas `git push` a main:
1. Railway detecta el cambio
2. Re-deploya automáticamente
3. En ~2 minutos está actualizado

**Super fácil!** 🎉

---

## 📝 Checklist de Deployment

- [ ] Código en GitHub
- [ ] Procfile creado
- [ ] runtime.txt creado
- [ ] gunicorn en requirements.txt
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas
- [ ] Base de datos inicializada
- [ ] Dominio generado
- [ ] URL actualizada en app Android
- [ ] Probado que funciona

---

## 🆘 Ayuda

Si algo sale mal:
1. Revisa los logs en Railway
2. Verifica que todos los archivos están en GitHub
3. Asegúrate que `.env` NO está en GitHub (.gitignore)
4. Railway Discord: https://discord.gg/railway

---

**¡Tu backend estará en la nube en menos de 10 minutos!** 🚀
