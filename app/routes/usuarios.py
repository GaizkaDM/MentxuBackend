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
    
    # Verificar si ya existe el device_id
    device_id = data.get('device_id')
    if device_id:
        usuario_existente = Usuario.query.filter_by(device_id=device_id).first()
        if usuario_existente:
            return jsonify({
                'mensaje': 'Usuario ya registrado',
                'usuario': usuario_existente.to_dict()
            }), 200
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        apellido=data['apellido'],
        device_id=device_id
    )
    
    try:
        db.session.add(nuevo_usuario)
        db.session.flush()  # Para obtener el ID antes de commit
        
        # Inicializar progreso con todas las paradas
        paradas = Parada.query.order_by(Parada.orden).all()
        for parada in paradas:
            estado = 'activa' if parada.orden == 1 else 'bloqueada'
            progreso = Progreso(
                usuario_id=nuevo_usuario.id,
                parada_id=parada.id,
                estado=estado,
                fecha_inicio=datetime.utcnow() if estado == 'activa' else None
            )
            db.session.add(progreso)
        
        db.session.commit()
        return jsonify({
            'mensaje': 'Usuario registrado correctamente',
            'usuario': nuevo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
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
