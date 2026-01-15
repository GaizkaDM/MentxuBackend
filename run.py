import os
from app import create_app

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando MentxuApp Backend Server")
    print("=" * 60)
    print(f"📍 Servidor corriendo en: http://localhost:5000")
    print(f"📍 Dashboard: http://localhost:5000/dashboard")
    print(f"📍 API REST: http://localhost:5000/api/paradas")
    print("=" * 60)
    print("\n⚠️  Usa CTRL+C para detener el servidor\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
