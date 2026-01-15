from flask import Blueprint, jsonify, request
from app import db
from app.models import Parada
from flask_login import login_required

paradas_bp = Blueprint('paradas', __name__)


@paradas_bp.route('/paradas', methods=['GET'])
def obtener_paradas():
    """Obtener todas las paradas (API pública)"""
    paradas = Parada.query.order_by(Parada.orden).all()
    return jsonify([parada.to_dict() for parada in paradas]), 200


@paradas_bp.route('/paradas/<int:id>', methods=['GET'])
def obtener_parada(id):
    """Obtener una parada específica"""
    parada = Parada.query.get_or_404(id)
    return jsonify(parada.to_dict()), 200


@paradas_bp.route('/paradas', methods=['POST'])
@login_required
def crear_parada():
    """Crear una nueva parada (requiere autenticación)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Validar campos requeridos
    campos_requeridos = ['nombre', 'latitud', 'longitud', 'orden']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'error': f'Campo requerido: {campo}'}), 400
    
    nueva_parada = Parada(
        nombre=data['nombre'],
        nombre_corto=data.get('nombre_corto', data['nombre']),
        latitud=data['latitud'],
        longitud=data['longitud'],
        descripcion=data.get('descripcion'),
        tipo_juego=data.get('tipo_juego'),
        orden=data['orden'],
        imagen_url=data.get('imagen_url')
    )
    
    try:
        db.session.add(nueva_parada)
        db.session.commit()
        return jsonify(nueva_parada.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paradas_bp.route('/paradas/<int:id>', methods=['PUT'])
@login_required
def actualizar_parada(id):
    """Actualizar una parada existente"""
    parada = Parada.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Actualizar campos
    if 'nombre' in data:
        parada.nombre = data['nombre']
    if 'nombre_corto' in data:
        parada.nombre_corto = data['nombre_corto']
    if 'latitud' in data:
        parada.latitud = data['latitud']
    if 'longitud' in data:
        parada.longitud = data['longitud']
    if 'descripcion' in data:
        parada.descripcion = data['descripcion']
    if 'tipo_juego' in data:
        parada.tipo_juego = data['tipo_juego']
    if 'orden' in data:
        parada.orden = data['orden']
    if 'imagen_url' in data:
        parada.imagen_url = data['imagen_url']
    
    try:
        db.session.commit()
        return jsonify(parada.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paradas_bp.route('/paradas/<int:id>', methods=['DELETE'])
@login_required
def eliminar_parada(id):
    """Eliminar una parada"""
    parada = Parada.query.get_or_404(id)
    
    try:
        db.session.delete(parada)
        db.session.commit()
        return jsonify({'mensaje': 'Parada eliminada correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paradas_bp.route('/paradas/<int:id>/estadisticas', methods=['GET'])
def estadisticas_parada(id):
    """Obtener estadísticas de una parada específica"""
    from app.models import Progreso
    from sqlalchemy import func
    
    parada = Parada.query.get_or_404(id)
    
    total_completados = Progreso.query.filter_by(
        parada_id=id, 
        estado='completada'
    ).count()
    
    total_activos = Progreso.query.filter_by(
        parada_id=id, 
        estado='activa'
    ).count()
    
    # Tiempo promedio
    tiempo_promedio = db.session.query(
        func.avg(Progreso.tiempo_empleado)
    ).filter(
        Progreso.parada_id == id,
        Progreso.estado == 'completada',
        Progreso.tiempo_empleado.isnot(None)
    ).scalar()
    
    return jsonify({
        'parada': parada.to_dict(),
        'total_completados': total_completados,
        'total_activos': total_activos,
        'tiempo_promedio_segundos': int(tiempo_promedio) if tiempo_promedio else 0
    }), 200
