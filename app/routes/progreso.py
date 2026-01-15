from flask import Blueprint, jsonify, request
from app import db
from app.models import Progreso, Parada, Usuario
from datetime import datetime

progreso_bp = Blueprint('progreso', __name__)


@progreso_bp.route('/progreso/<int:usuario_id>', methods=['GET'])
def obtener_progreso(usuario_id):
    """Obtener el progreso completo de un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    progresos = Progreso.query.filter_by(usuario_id=usuario_id).join(Parada).order_by(Parada.orden).all()
    
    return jsonify({
        'usuario_id': usuario_id,
        'nombre_completo': f"{usuario.nombre} {usuario.apellido}",
        'progreso': [p.to_dict() for p in progresos]
    }), 200


@progreso_bp.route('/progreso/completar', methods=['POST'])
def completar_parada():
    """Marcar una parada como completada y activar la siguiente"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    usuario_id = data.get('usuario_id')
    parada_id = data.get('parada_id')
    
    if not usuario_id or not parada_id:
        return jsonify({'error': 'usuario_id y parada_id son requeridos'}), 400
    
    # Obtener el progreso actual
    progreso_actual = Progreso.query.filter_by(
        usuario_id=usuario_id,
        parada_id=parada_id
    ).first()
    
    if not progreso_actual:
        return jsonify({'error': 'Progreso no encontrado'}), 404
    
    if progreso_actual.estado == 'completada':
        return jsonify({'mensaje': 'Esta parada ya fue completada'}), 200
    
    # Marcar como completada
    progreso_actual.estado = 'completada'
    progreso_actual.fecha_completado = datetime.utcnow()
    
    # Actualizar métricas opcionales
    if 'puntuacion' in data:
        progreso_actual.puntuacion = data['puntuacion']
    if 'tiempo_empleado' in data:
        progreso_actual.tiempo_empleado = data['tiempo_empleado']
    if 'intentos' in data:
        progreso_actual.intentos = data['intentos']
    
    try:
        # Activar la siguiente parada
        parada_actual = Parada.query.get(parada_id)
        siguiente_parada = Parada.query.filter(Parada.orden > parada_actual.orden).order_by(Parada.orden).first()
        
        if siguiente_parada:
            progreso_siguiente = Progreso.query.filter_by(
                usuario_id=usuario_id,
                parada_id=siguiente_parada.id
            ).first()
            
            if progreso_siguiente and progreso_siguiente.estado == 'bloqueada':
                progreso_siguiente.estado = 'activa'
                progreso_siguiente.fecha_inicio = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Parada completada correctamente',
            'progreso': progreso_actual.to_dict(),
            'siguiente_parada_id': siguiente_parada.id if siguiente_parada else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@progreso_bp.route('/progreso/<int:id>', methods=['PUT'])
def actualizar_progreso(id):
    """Actualizar un progreso específico"""
    progreso = Progreso.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Actualizar campos permitidos
    if 'puntuacion' in data:
        progreso.puntuacion = data['puntuacion']
    if 'tiempo_empleado' in data:
        progreso.tiempo_empleado = data['tiempo_empleado']
    if 'intentos' in data:
        progreso.intentos = data['intentos']
    
    try:
        db.session.commit()
        return jsonify(progreso.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@progreso_bp.route('/estadisticas', methods=['GET'])
def estadisticas_generales():
    """Obtener estadísticas generales del sistema"""
    from sqlalchemy import func
    
    total_usuarios = Usuario.query.count()
    total_paradas = Parada.query.count()
    total_completados = Progreso.query.filter_by(estado='completada').count()
    total_activos = Progreso.query.filter_by(estado='activa').count()
    
    # Parada más completada
    parada_popular = db.session.query(
        Parada.nombre_corto,
        func.count(Progreso.id).label('total')
    ).join(Progreso).filter(
        Progreso.estado == 'completada'
    ).group_by(Parada.id).order_by(func.count(Progreso.id).desc()).first()
    
    # Usuarios que completaron todo
    usuarios_completaron_todo = db.session.query(Usuario.id).join(Progreso).filter(
        Progreso.estado == 'completada'
    ).group_by(Usuario.id).having(
        func.count(Progreso.id) == total_paradas
    ).count()
    
    return jsonify({
        'total_usuarios': total_usuarios,
        'total_paradas': total_paradas,
        'total_completados': total_completados,
        'total_activos': total_activos,
        'parada_mas_popular': parada_popular[0] if parada_popular else None,
        'usuarios_completaron_todo': usuarios_completaron_todo
    }), 200
