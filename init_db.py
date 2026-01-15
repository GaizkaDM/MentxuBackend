from app import create_app, db
from app.models import Admin, Parada
from config import config
import os

def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    
    app = create_app('default')
    
    with app.app_context():
        # Crear todas las tablas
        print("📦 Creando tablas en la base de datos...")
        db.create_all()
        
        # Crear usuario administrador si no existe
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            print("👤 Creando usuario administrador...")
            admin = Admin(username='admin', email='admin@mentxuapp.com')
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Usuario creado: admin / admin123")
        else:
            print("ℹ️  Usuario admin ya existe")
        
        # Crear las 6 paradas de Santurtzi si no existen
        if Parada.query.count() == 0:
            print("🗺️  Creando las 6 paradas de Santurtzi...")
            
            paradas_data = [
                {
                    'orden': 1,
                    'nombre': 'Santurtziko Udala (Mentxu)',
                    'nombre_corto': 'Ayuntamiento',
                    'latitud': 43.328833,
                    'longitud': -3.032944,
                    'tipo_juego': 'sopa_letras',
                    'descripcion': 'El ayuntamiento de Santurtzi, punto de partida del recorrido. Incluye una sopa de letras y un huevo de pascua con audio.'
                },
                {
                    'orden': 2,
                    'nombre': '"El niño y el perro" eskultura',
                    'nombre_corto': 'Escultura El Niño y el Perro',
                    'latitud': 43.328833,
                    'longitud': -3.032306,
                    'tipo_juego': 'diferencias',
                    'descripcion': 'Icónica escultura del puerto. Juego de encontrar las 7 diferencias en imágenes del puerto.'
                },
                {
                    'orden': 3,
                    'nombre': 'Agurtza itsasontzia',
                    'nombre_corto': 'Barco Agurtza',
                    'latitud': 43.327000,
                    'longitud': -3.023778,
                    'tipo_juego': 'relacionar',
                    'descripcion': 'El histórico barco Agurtza. Juego de relacionar elementos marítimos.'
                },
                {
                    'orden': 4,
                    'nombre': 'Itsas-museoa',
                    'nombre_corto': 'Museo Marítimo',
                    'latitud': 43.330639,
                    'longitud': -3.030750,
                    'tipo_juego': 'recogida',
                    'descripcion': 'Museo dedicado a la historia pesquera de Santurtzi. Juego de recoger basura del mar.'
                },
                {
                    'orden': 5,
                    'nombre': 'Itsas-portua',
                    'nombre_corto': 'Puerto',
                    'latitud': 43.330417,
                    'longitud': -3.030722,
                    'tipo_juego': 'pesca',
                    'descripcion': 'El puerto pesquero, corazón de Santurtzi. Juego de proceso de pesca.'
                },
                {
                    'orden': 6,
                    'nombre': '"Monumento niños y niñas de la guerra" eskultura',
                    'nombre_corto': 'Monumento Niños de la Guerra',
                    'latitud': 43.330500,
                    'longitud': -3.029917,
                    'tipo_juego': 'puzzle',
                    'descripcion': 'Monumento conmemorativo. Parada final del recorrido turístico.'
                }
            ]
            
            for parada_data in paradas_data:
                parada = Parada(**parada_data)
                db.session.add(parada)
                print(f"   ✓ Parada {parada_data['orden']}: {parada_data['nombre_corto']}")
        else:
            print("ℹ️  Las paradas ya existen")
        
        # Commit de todos los cambios
        db.session.commit()
        
        print("\n✅ Base de datos inicializada correctamente!")
        print("\n📝 Información de acceso:")
        print("   URL: http://localhost:5000")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n🗺️  Paradas creadas: 6")
        print("\n🚀 Ejecuta 'python run.py' para iniciar el servidor\n")


if __name__ == '__main__':
    init_database()
