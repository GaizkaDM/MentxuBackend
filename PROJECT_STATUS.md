# 📝 Estado de Archivos del Proyecto MentxuApp Backend

## ✅ **Archivos ESENCIALES (Necesarios)**

### **Para Railway (Deployment)**
```
Procfile                    ✅ Dice a Railway cómo ejecutar la app
runtime.txt                 ✅ Versión de Python
requirements.txt            ✅ Dependencias Python
config.py                   ✅ Configuración (SQLite local + PostgreSQL producción)
app/__init__.py             ✅ Factory de Flask + Auto-inicialización de BD
```

### **Para la Aplicación**
```
app/
  __init__.py               ✅ Inicialización de app + BD auto
  models.py                 ✅ Modelos de base de datos
  routes/                   ✅ Todos los blueprints (web, API)
    web.py
    auth.py
    paradas.py
    usuarios.py
    progreso.py
  templates/                ✅ HTML del panel web
  static/                   ✅ CSS, JS, imágenes
```

### **Para Control de Versiones**
```
.gitignore                  ✅ Evita subir archivos sensibles
README.md                   ✅ Documentación principal
QUICKSTART.md               ✅ Guía rápida
```

---

## ⚠️ **Archivos LEGACY (Opcionales/Ya no necesarios)**

### **init_db.py**
```
Estado: OPCIONAL
Razón: La BD se auto-inicializa en app/__init__.py
Mantener: Solo si quieres reiniciar la BD manualmente en desarrollo
Eliminar: git rm init_db.py (si no lo usas)
```

### **instance/mentxuapp.db**
```
Estado: SOLO DESARROLLO LOCAL
Razón: En Railway usas PostgreSQL, no SQLite
Mantener: Solo existe en tu máquina local
En .gitignore: ✅ Ya está ignorado
```

---

## 📊 **Resumen de Cambios**

### **Antes:**
```
- SQLite en Railway (datos efímeros ❌)
- init_db.py manual para crear BD
- run.py con lógica de inicialización
```

### **Ahora:**
```
- PostgreSQL en Railway (datos persistentes ✅)
- Auto-inicialización en app/__init__.py
- run.py limpio, solo para desarrollo local
- Soporte dual: SQLite (dev) + PostgreSQL (prod)
```

---

## 🗑️ **Archivos que PUEDES eliminar (opcional)**

Si quieres hacer limpieza:

```powershell
cd c:\Users\GaizkaClase\Desktop\MentxuBackend

# Eliminar init_db.py (opcional, ya no se usa)
git rm init_db.py

# Commit
git commit -m "Remove legacy init_db.py"
git push origin main
```

**PERO** te recomiendo **mantenerlo** por si alguna vez necesitas:
- Resetear la BD local durante desarrollo
- Volver a llenar con datos de prueba
- Debugging

---

## 📂 **Estructura Final Limpia**

```
MentxuBackend/
├── Procfile                    # Railway: cómo ejecutar
├── runtime.txt                 # Railway: Python version
├── requirements.txt            # Dependencias (con psycopg2)
├── .gitignore                  # Ignorar archivos
├── .env.example                # Template de variables
├── config.py                   # Config (SQLite + PostgreSQL)
├── run.py                      # Desarrollo local
├── init_db.py                  # LEGACY (opcional)
├── app/
│   ├── __init__.py             # ⭐ Auto-init BD aquí
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   └── static/
├── instance/                   # Solo local (en .gitignore)
│   └── mentxuapp.db           # SQLite local
├── README.md
├── QUICKSTART.md
├── RAILWAY_DEPLOYMENT.md
└── PROYECTO_RESUMEN.md
```

---

## ✅ **Archivos Críticos que NO debes tocar:**

❌ **NO elimines:**
- Procfile
- runtime.txt
- requirements.txt
- app/__init__.py
- config.py
- Cualquier cosa en app/routes/
- Cualquier cosa en app/templates/

✅ **Puedes eliminar sin problemas:**
- init_db.py (ya no se usa en Railway)
- instance/ folder (solo local, ya en .gitignore)

---

## 🎯 **Recomendación:**

**Mantén init_db.py** por ahora. Es útil tenerlo como referencia o para desarrollo.

**Lo importante:**
✅ Railway usa PostgreSQL (persistente)
✅ Auto-inicialización funciona
✅ Código limpio en run.py
✅ Todo está documentado

---

¿Quieres que elimine `init_db.py` o lo dejamos como está?
