import os
from app import create_app

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'default'))

def init_db_if_needed():
    """Inicializa la base de datos si no existe (para Railway/Producción)"""
    db_path = os.path.join('instance', 'mentxuapp.db')
    
    if not os.path.exists(db_path):
        print("🔄 Base de datos no encontrada. Inicializando...")
        
        from app import db
        from app.models import Admin, Parada
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Crear tablas
            db.create_all()
            print("✅ Tablas creadas")
            
            # Crear admin por defecto
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            if not Admin.query.filter_by(username=admin_username).first():
                admin = Admin(username=admin_username)
                admin.set_password(admin_password)
                db.session.add(admin)
                print(f"✅ Admin creado: {admin_username}")
            
            # Crear paradas de Santurtzi
            if Parada.query.count() == 0:
                paradas_data = [
                    {'nombre': 'Ayuntamiento de Santurtzi (Mentxu)', 'nombre_corto': 'Ayuntamiento',
                     'latitud': 43.3289, 'longitud': -3.0323, 'descripcion': 'Punto de inicio del recorrido',
                     'tipo_juego': 'Sopa de Letras', 'orden': 1},
                    {'nombre': 'Escultura "El niño y el perro"', 'nombre_corto': 'Escultura',
                     'latitud': 43.3275, 'longitud': -3.0310, 'descripcion': 'Famosa escultura cerca del puerto',
                     'tipo_juego': 'Encuentra las Diferencias', 'orden': 2},
                    {'nombre': 'Barco Agurtza', 'nombre_corto': 'Barco',
                     'latitud': 43.3265, 'longitud': -3.0295, 'descripcion': 'Histórico barco en el puerto',
                     'tipo_juego': 'Relacionar', 'orden': 3},
                    {'nombre': 'Museo Marítimo Itsasmuseum', 'nombre_corto': 'Museo',
                     'latitud': 43.3258, 'longitud': -3.0288, 'descripcion': 'Museo dedicado a la historia marítima',
                     'tipo_juego': 'Recogida de Basura', 'orden': 4},
                    {'nombre': 'Puerto Pesquero', 'nombre_corto': 'Puerto',
                     'latitud': 43.3270, 'longitud': -3.0305, 'descripcion': 'Activo puerto pesquero',
                     'tipo_juego': 'Proceso de Pesca', 'orden': 5},
                    {'nombre': 'Monumento a los Niños de la Guerra', 'nombre_corto': 'Monumento',
                     'latitud': 43.3280, 'longitud': -3.0315, 'descripcion': 'Conmemoración histórica',
                     'tipo_juego': 'Puzzle', 'orden': 6}
                ]
                
                for p in paradas_data:
                    db.session.add(Parada(**p))
                print(f"✅ {len(paradas_data)} paradas creadas")
            
            db.session.commit()
            print("✅ Base de datos inicializada correctamente")
    else:
        print("✅ Base de datos ya existe")

if __name__ == '__main__':
    # Inicializar BD automáticamente
    init_db_if_needed()
    
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
