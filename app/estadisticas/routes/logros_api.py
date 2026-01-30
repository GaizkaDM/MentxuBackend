# ==============================================================================
# 📊 API REST - SISTEMA DE LOGROS
# ==============================================================================
#
# Endpoints para gestionar logros:
#   - GET /api/logros                    - Listar todos los logros
#   - GET /api/logros/<id>               - Obtener un logro
#   - GET /api/logros/usuario/<id>       - Logros de un usuario
#   - POST /api/logros/desbloquear       - Desbloquear logro
#   - POST /api/logros/verificar/<id>    - Verificar logros del usuario
#
# ==============================================================================

from flask import Blueprint, jsonify, request
from datetime import datetime

logros_api_bp = Blueprint('logros_api', __name__, url_prefix='/api/logros')


@logros_api_bp.route('', methods=['GET'])
def listar_logros():
    """
    Lista todos los logros disponibles.
    
    Query params:
        - tipo: Filtrar por tipo (velocidad, precision, etc.)
        - incluir_secretos: true/false
        - activos_solo: true/false
    
    Returns:
        Lista de logros
    """
    from ..models import Logro, TipoLogro
    
    try:
        tipo = request.args.get('tipo')
        incluir_secretos = request.args.get('incluir_secretos', 'false').lower() == 'true'
        activos_solo = request.args.get('activos_solo', 'true').lower() == 'true'
        
        query = Logro.query
        
        if activos_solo:
            query = query.filter_by(activo=True)
        
        if not incluir_secretos:
            query = query.filter_by(secreto=False)
        
        if tipo:
            try:
                tipo_enum = TipoLogro(tipo)
                query = query.filter_by(tipo=tipo_enum)
            except ValueError:
                pass
        
        logros = query.order_by(Logro.orden, Logro.id).all()
        
        return jsonify({
            'logros': [l.to_dict() for l in logros],
            'total': len(logros)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/<int:logro_id>', methods=['GET'])
def obtener_logro(logro_id: int):
    """
    Obtiene los detalles de un logro específico.
    
    Args:
        logro_id: ID del logro
    
    Returns:
        Detalles del logro
    """
    from ..models import Logro
    
    try:
        logro = Logro.query.get_or_404(logro_id)
        
        return jsonify({
            'logro': logro.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def logros_usuario(usuario_id: int):
    """
    Obtiene los logros de un usuario.
    
    Args:
        usuario_id: ID del usuario
    
    Query params:
        - solo_completados: true/false
        - incluir_todos: true/false (incluir no desbloqueados)
    
    Returns:
        Logros del usuario con estado
    """
    from ..models import Logro, LogroUsuario
    from app.models import Usuario
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        solo_completados = request.args.get('solo_completados', 'false').lower() == 'true'
        incluir_todos = request.args.get('incluir_todos', 'true').lower() == 'true'
        
        # Obtener logros del usuario
        logros_desbloqueados = LogroUsuario.get_logros_usuario(
            usuario_id=usuario_id,
            solo_completados=solo_completados
        )
        
        # Mapear por ID
        logros_map = {}
        for lu in logros_desbloqueados:
            logros_map[lu.logro_id] = {
                'logro': lu.logro.to_dict_para_usuario(desbloqueado=lu.progreso >= 100),
                'fecha_desbloqueo': lu.fecha_desbloqueo.isoformat() if lu.progreso >= 100 else None,
                'progreso': lu.progreso,
                'desbloqueado': lu.progreso >= 100
            }
        
        if incluir_todos:
            # Incluir logros no desbloqueados
            todos_logros = Logro.query.filter_by(activo=True).order_by(Logro.orden).all()
            
            resultado = []
            for logro in todos_logros:
                if logro.id in logros_map:
                    resultado.append(logros_map[logro.id])
                else:
                    resultado.append({
                        'logro': logro.to_dict_para_usuario(desbloqueado=False),
                        'fecha_desbloqueo': None,
                        'progreso': 0,
                        'desbloqueado': False
                    })
        else:
            resultado = list(logros_map.values())
        
        # Estadísticas
        estadisticas = LogroUsuario.get_estadisticas_usuario(usuario_id)
        
        return jsonify({
            'usuario': usuario.to_dict(),
            'logros': resultado,
            'estadisticas': estadisticas
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/desbloquear', methods=['POST'])
def desbloquear_logro():
    """
    Desbloquea un logro para un usuario.
    
    Body JSON:
        - usuario_id: ID del usuario (requerido)
        - logro_id: ID del logro (requerido)
        - progreso: Progreso 0-100 (opcional, default 100)
    
    Returns:
        Logro desbloqueado
    """
    from ..models import Logro, LogroUsuario
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        usuario_id = data.get('usuario_id')
        logro_id = data.get('logro_id')
        progreso = data.get('progreso', 100)
        
        if not usuario_id or not logro_id:
            return jsonify({'error': 'usuario_id y logro_id son requeridos'}), 400
        
        # Verificar que el logro existe
        logro = Logro.query.get(logro_id)
        if not logro:
            return jsonify({'error': 'Logro no encontrado'}), 404
        
        # Desbloquear
        logro_usuario = LogroUsuario.desbloquear(
            usuario_id=usuario_id,
            logro_id=logro_id,
            progreso=progreso
        )
        
        es_nuevo = logro_usuario.progreso >= 100 and not logro_usuario.notificado
        
        return jsonify({
            'mensaje': 'Logro desbloqueado' if logro_usuario.progreso >= 100 else 'Progreso actualizado',
            'logro_usuario': logro_usuario.to_dict(include_relations=True),
            'es_nuevo': es_nuevo,
            'puntos_ganados': logro.puntos if es_nuevo else 0
        }), 201 if es_nuevo else 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/verificar/<int:usuario_id>', methods=['POST'])
def verificar_logros(usuario_id: int):
    """
    Verifica y desbloquea automáticamente los logros que el usuario ha conseguido.
    
    Esta función analiza las estadísticas actuales del usuario
    y desbloquea cualquier logro cuyos requisitos se cumplan.
    
    Args:
        usuario_id: ID del usuario
    
    Returns:
        Lista de logros nuevos desbloqueados
    """
    from ..models import Logro, LogroUsuario, HistorialIntento, Sesion
    from app.models import Usuario, Progreso
    from app import db
    from sqlalchemy import func
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Recopilar estadísticas del usuario
        stats = {}
        
        # Paradas completadas
        paradas_completadas = Progreso.query.filter_by(
            usuario_id=usuario_id,
            estado='completada'
        ).count()
        stats['paradas_completadas'] = paradas_completadas
        
        # Puntuaciones perfectas
        perfectas = HistorialIntento.query.filter(
            HistorialIntento.usuario_id == usuario_id,
            HistorialIntento.puntuacion == 100
        ).count()
        stats['puntuacion_perfecta'] = perfectas
        
        # Paradas rápidas (menos de 60 segundos)
        from ..models import ResultadoIntento
        paradas_rapidas = HistorialIntento.query.filter(
            HistorialIntento.usuario_id == usuario_id,
            HistorialIntento.tiempo_segundos <= 60,
            HistorialIntento.resultado == ResultadoIntento.EXITO
        ).count()
        stats['paradas_rapidas'] = paradas_rapidas
        
        # Sesiones totales
        sesiones = Sesion.query.filter_by(usuario_id=usuario_id).count()
        stats['sesiones_totales'] = sesiones
        
        # Logros ya desbloqueados
        logros_actuales = LogroUsuario.query.filter_by(
            usuario_id=usuario_id
        ).with_entities(LogroUsuario.logro_id).all()
        logros_actuales_ids = {lu.logro_id for lu in logros_actuales}
        
        # Total de logros (para el logro de coleccionista)
        total_logros = Logro.query.filter_by(activo=True).count()
        stats['porcentaje_logros'] = (len(logros_actuales_ids) / (total_logros - 1)) * 100 if total_logros > 1 else 0
        
        # Verificar cada logro
        nuevos_desbloqueados = []
        
        for logro in Logro.query.filter_by(activo=True).all():
            # Saltar si ya está desbloqueado
            if logro.id in logros_actuales_ids:
                continue
            
            # Verificar requisitos
            if logro.verificar_requisitos(stats):
                logro_usuario = LogroUsuario.desbloquear(
                    usuario_id=usuario_id,
                    logro_id=logro.id,
                    progreso=100
                )
                
                # Formato compatible con Android
                nuevos_desbloqueados.append({
                    'id': logro.id,
                    'nombre': logro.nombre,
                    'descripcion': logro.descripcion,
                    'tipo': logro.tipo.value if logro.tipo else None,
                    'puntos': logro.puntos,
                    'icono': logro.icono,
                    'color': logro.color
                })
        
        # Calcular puntos totales ganados
        puntos_ganados = sum(l['puntos'] for l in nuevos_desbloqueados)
        
        return jsonify({
            'usuario_id': usuario_id,
            'nuevos_logros': nuevos_desbloqueados,  # Compatible con Android DTO
            'nuevos_desbloqueados': nuevos_desbloqueados,  # Mantener compatibilidad
            'total_verificados': len(Logro.query.filter_by(activo=True).all()),
            'cantidad': len(nuevos_desbloqueados),
            'puntos_ganados': puntos_ganados,
            'estadisticas_actuales': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/notificados/<int:usuario_id>', methods=['GET'])
def logros_pendientes_notificar(usuario_id: int):
    """
    Obtiene los logros pendientes de notificar al usuario.
    
    Returns:
        Lista de logros no notificados
    """
    from ..models import LogroUsuario
    
    try:
        pendientes = LogroUsuario.get_pendientes_notificar(usuario_id)
        
        return jsonify({
            'pendientes': [
                {
                    'logro': lu.logro.to_dict(),
                    'fecha_desbloqueo': lu.fecha_desbloqueo.isoformat()
                }
                for lu in pendientes
            ],
            'cantidad': len(pendientes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/notificar/<int:logro_usuario_id>', methods=['POST'])
def marcar_notificado(logro_usuario_id: int):
    """
    Marca un logro como notificado.
    
    Args:
        logro_usuario_id: ID del registro LogroUsuario
    """
    from ..models import LogroUsuario
    
    try:
        logro_usuario = LogroUsuario.query.get_or_404(logro_usuario_id)
        logro_usuario.marcar_notificado()
        
        return jsonify({
            'mensaje': 'Marcado como notificado',
            'logro_usuario_id': logro_usuario_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/puntos/<int:usuario_id>', methods=['GET'])
def puntos_usuario(usuario_id: int):
    """
    Obtiene los puntos totales del usuario por logros.
    
    Args:
        usuario_id: ID del usuario
    
    Returns:
        Total de puntos y desglose
    """
    from ..models import LogroUsuario, Logro
    from app import db
    from sqlalchemy import func
    
    try:
        puntos_totales = LogroUsuario.get_puntos_totales(usuario_id)
        
        # Desglose por tipo
        desglose = db.session.query(
            Logro.tipo,
            func.sum(Logro.puntos).label('puntos')
        ).join(LogroUsuario).filter(
            LogroUsuario.usuario_id == usuario_id,
            LogroUsuario.progreso >= 100
        ).group_by(Logro.tipo).all()
        
        return jsonify({
            'usuario_id': usuario_id,
            'puntos_totales': puntos_totales,
            'desglose': {
                str(t.value): int(p or 0) for t, p in desglose
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@logros_api_bp.route('/inicializar', methods=['POST'])
def inicializar_logros():
    """
    Inicializa los logros predefinidos en el sistema.
    Solo para administración.
    """
    from ..models import Logro
    
    try:
        creados = Logro.crear_logros_predefinidos()
        
        return jsonify({
            'mensaje': f'Se crearon {len(creados)} logros',
            'logros': [l.to_dict() for l in creados]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
