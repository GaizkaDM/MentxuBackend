from flask import Blueprint, jsonify, request
from app import db
from app.models import Usuario, Progreso, Parada
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    """Obtener todos los usuarios"""
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return jsonify([usuario.to_dict() for usuario in usuarios]), 200


@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    """Obtener un usuario específico"""
    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario.to_dict()), 200


@usuarios_bp.route('/usuarios/registro', methods=['POST'])
def registrar_usuario():
    """Registrar un nuevo usuario desde la app móvil"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Validar campos requeridos
    if 'nombre' not in data or 'apellido' not in data:
        return jsonify({'error': 'Nombre y apellido son requeridos'}), 400
    
    # Obtener datos del usuario
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    device_id = data.get('device_id')
    avatar = data.get('avatar', 'perro')  # Valor por defecto
    color_favorito = data.get('color_favorito', 'azul')  # Valor por defecto
    
    # Validar avatar y color
    avatares_validos = ['perro', 'gato', 'conejo', 'zorro', 'oso', 'panda', 'leon', 'unicornio']
    colores_validos = ['rojo', 'azul', 'verde', 'amarillo', 'morado', 'naranja', 'rosa']
    
    if avatar not in avatares_validos:
        avatar = 'perro'
    if color_favorito not in colores_validos:
        color_favorito = 'azul'
    
    # Lógica Inteligente: buscar si ya existe este usuario exacto
    # La combinación nombre + apellido + avatar + color identifica al usuario
    usuario = Usuario.query.filter_by(
        nombre=nombre, 
        apellido=apellido,
        avatar=avatar,
        color_favorito=color_favorito
    ).first()
    
    if not usuario:
        # Si no existe, lo creamos
        print(f"🆕 Creando nuevo usuario: {nombre} ({avatar}, {color_favorito})")
        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            device_id=device_id,
            avatar=avatar,
            color_favorito=color_favorito
        )
        db.session.add(usuario)
        db.session.flush()
    else:
        # Actualizar el device_id si cambió (usuario recuperado en otro dispositivo)
        if usuario.device_id != device_id:
            usuario.device_id = device_id
            print(f"📱 Actualizando device_id para usuario {nombre}")
        print(f"♻️ Recuperando usuario existente: {nombre} ({avatar}, {color_favorito})")
    
    try:
        # Inicializar progreso solo si no tiene (por si se reseteó la BD)
        progresos_existentes = Progreso.query.filter_by(usuario_id=usuario.id).count()
        
        if progresos_existentes == 0:
            print(f"🔄 Inicializando progreso para usuario {usuario.id}...")
            paradas = Parada.query.order_by(Parada.orden).all()
            for parada in paradas:
                estado = 'activa' if parada.orden == 1 else 'bloqueada'
                progreso = Progreso(
                    usuario_id=usuario.id,
                    parada_id=parada.id,
                    estado=estado,
                    fecha_inicio=datetime.utcnow() if estado == 'activa' else None
                )
                db.session.add(progreso)
            db.session.commit()
            print(f"✅ Progreso verificado/creado para usuario {usuario.id}")
        
        return jsonify({
            'mensaje': 'Usuario procesado correctamente',
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en registro: {str(e)}")
        return jsonify({'error': str(e)}), 500


@usuarios_bp.route('/usuarios/<int:id>/progreso', methods=['GET'])
def obtener_progreso_usuario(id):
    """Obtener el progreso completo de un usuario"""
    usuario = Usuario.query.get_or_404(id)
    progresos = Progreso.query.filter_by(usuario_id=id).join(Parada).order_by(Parada.orden).all()
    
    return jsonify({
        'usuario': usuario.to_dict(),
        'progreso': [p.to_dict() for p in progresos]
    }), 200


@usuarios_bp.route('/ranking', methods=['GET'])
def obtener_ranking():
    """Obtener el ranking de usuarios basado en la puntuación total"""
    from sqlalchemy import func
    
    # Obtenemos la suma de puntuaciones de paradas completadas por cada usuario
    ranking = db.session.query(
        Usuario.id,
        Usuario.nombre,
        Usuario.apellido,
        Usuario.avatar,
        Usuario.color_favorito,
        func.sum(Progreso.puntuacion).label('puntuacion_total'),
        func.count(Progreso.id).label('paradas_completadas')
    ).join(Progreso).filter(Progreso.estado == 'completada')\
     .group_by(Usuario.id, Usuario.nombre, Usuario.apellido, Usuario.avatar, Usuario.color_favorito)\
     .order_by(func.sum(Progreso.puntuacion).desc())\
     .limit(100).all()
    
    resultado = []
    for pos, row in enumerate(ranking, 1):
        resultado.append({
            'posicion': pos,
            'usuario_id': row.id,
            'nombre': f"{row.nombre} {row.apellido}",
            'avatar': row.avatar,
            'color_favorito': row.color_favorito,
            'puntuacion_total': int(row.puntuacion_total or 0),
            'paradas_completadas': row.paradas_completadas
        })
    
    return jsonify(resultado), 200


@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    """Eliminar un usuario (solo para administración)"""
    usuario = Usuario.query.get_or_404(id)
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
