# ==============================================================================
# 📊 API REST - ESTADÍSTICAS GENERALES
# ==============================================================================
#
# Endpoints para consultar estadísticas:
#   - GET /api/stats/general         - Estadísticas globales
#   - GET /api/stats/usuarios/<id>   - Estadísticas de un usuario
#   - GET /api/stats/paradas/<id>    - Estadísticas de una parada
#   - GET /api/stats/sesiones        - Estadísticas de sesiones
#   - GET /api/stats/actividades     - Estadísticas de actividades
#
# ==============================================================================

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

estadisticas_api_bp = Blueprint('estadisticas_api', __name__, url_prefix='/api/stats')


@estadisticas_api_bp.route('/diagnostico', methods=['GET'])
def diagnostico():
    """Endpoint de diagnóstico para verificar estado de las tablas."""
    from app import db
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(db.engine)
        tablas_existentes = inspector.get_table_names()
        
        tablas_estadisticas = ['sesion', 'logro', 'logro_usuario', 'historial_intento']
        estado_tablas = {t: t in tablas_existentes for t in tablas_estadisticas}
        
        return jsonify({
            'estado': 'ok',
            'tablas_sistema': tablas_existentes[:20],  # Primeras 20
            'tablas_estadisticas': estado_tablas,
            'todas_existen': all(estado_tablas.values())
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/crear-tablas', methods=['POST'])
def crear_tablas():
    """Fuerza la creación de tablas de estadísticas."""
    from app import db
    from ..models import Sesion, Logro, LogroUsuario, HistorialIntento
    
    try:
        db.create_all()
        return jsonify({
            'mensaje': 'Tablas creadas correctamente',
            'tablas': ['sesion', 'logro', 'logro_usuario', 'historial_intento']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/reset-datos', methods=['POST'])
def reset_datos():
    """
    ⚠️ PELIGRO: Borra TODOS los datos de usuarios y estadísticas.
    BORRAR ESTE ENDPOINT DESPUÉS DE USARLO.
    
    Body JSON opcional:
        - confirmar: debe ser "BORRAR_TODO" para ejecutar
    """
    from app import db
    from app.models import Usuario, Progreso
    from ..models import Sesion, Logro, LogroUsuario, HistorialIntento
    
    try:
        data = request.get_json() or {}
        
        # Requiere confirmación para evitar borrados accidentales
        if data.get('confirmar') != 'BORRAR_TODO':
            return jsonify({
                'error': 'Debes enviar {"confirmar": "BORRAR_TODO"} para confirmar',
                'advertencia': '⚠️ Esto borrará TODOS los datos de usuarios y estadísticas'
            }), 400
        
        # Borrar en orden para respetar foreign keys
        deleted = {}
        deleted['historial_intento'] = HistorialIntento.query.delete()
        deleted['logro_usuario'] = LogroUsuario.query.delete()
        deleted['sesiones'] = Sesion.query.delete()
        deleted['progreso'] = Progreso.query.delete()
        deleted['usuarios'] = Usuario.query.delete()
        
        db.session.commit()
        
        return jsonify({
            'mensaje': '✅ Todos los datos borrados correctamente',
            'registros_eliminados': deleted,
            'advertencia': '⚠️ BORRA ESTE ENDPOINT del código por seguridad'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/general', methods=['GET'])
def estadisticas_generales():
    """
    Obtiene estadísticas generales del sistema.
    
    Query params:
        - desde: Fecha inicio (ISO format)
        - hasta: Fecha fin (ISO format)
    
    Returns:
        JSON con estadísticas globales
    """
    from app.models import Usuario, Parada, Progreso
    from ..models import Sesion, HistorialIntento, LogroUsuario
    from sqlalchemy import func
    from app import db
    
    try:
        # Usuarios
        total_usuarios = Usuario.query.count()
        usuarios_activos_7d = db.session.query(
            func.count(func.distinct(Sesion.usuario_id))
        ).filter(
            Sesion.fecha_inicio >= datetime.utcnow() - timedelta(days=7)
        ).scalar() or 0
        
        # Paradas
        total_paradas = Parada.query.count()
        total_completadas = Progreso.query.filter_by(estado='completada').count()
        
        # Sesiones
        sesiones_stats = Sesion.get_estadisticas_generales()
        
        # Intentos
        intentos_stats = HistorialIntento.get_estadisticas_generales()
        
        # Tasa de completado
        tasa_completado = 0
        if total_usuarios > 0 and total_paradas > 0:
            tasa_completado = (total_completadas / (total_usuarios * total_paradas)) * 100
        
        return jsonify({
            'usuarios': {
                'total': total_usuarios,
                'activos_ultima_semana': usuarios_activos_7d
            },
            'paradas': {
                'total': total_paradas,
                'completadas_total': total_completadas,
                'tasa_completado': round(tasa_completado, 2)
            },
            'sesiones': sesiones_stats,
            'actividades': intentos_stats,
            'fecha_consulta': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
def estadisticas_usuario(usuario_id: int):
    """
    Obtiene estadísticas completas de un usuario.
    
    Args:
        usuario_id: ID del usuario
    
    Returns:
        JSON con estadísticas del usuario
    """
    from app.models import Usuario, Progreso
    from ..models import Sesion, HistorialIntento, LogroUsuario
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        
        # Estadísticas de cada tipo
        sesiones_stats = Sesion.get_estadisticas_usuario(usuario_id)
        intentos_stats = HistorialIntento.get_estadisticas_usuario(usuario_id)
        logros_stats = LogroUsuario.get_estadisticas_usuario(usuario_id)
        
        # Progreso en paradas
        progresos = Progreso.query.filter_by(usuario_id=usuario_id).all()
        paradas_completadas = len([p for p in progresos if p.estado == 'completada'])
        paradas_activas = len([p for p in progresos if p.estado == 'activa'])
        
        return jsonify({
            'usuario': usuario.to_dict(),
            'sesiones': sesiones_stats,
            'actividades': intentos_stats,
            'logros': logros_stats,
            'progreso_paradas': {
                'completadas': paradas_completadas,
                'activas': paradas_activas,
                'total': len(progresos)
            },
            'fecha_consulta': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/paradas/<int:parada_id>', methods=['GET'])
def estadisticas_parada(parada_id: int):
    """
    Obtiene estadísticas de una parada/actividad.
    
    Args:
        parada_id: ID de la parada
    
    Returns:
        JSON con estadísticas de la parada
    """
    from app.models import Parada, Progreso
    from ..models import HistorialIntento
    from sqlalchemy import func
    from app import db
    
    try:
        parada = Parada.query.get_or_404(parada_id)
        
        # Estadísticas de intentos
        intentos_stats = HistorialIntento.get_estadisticas_parada(parada_id)
        
        # Progreso de usuarios
        progresos = Progreso.query.filter_by(parada_id=parada_id).all()
        completados = len([p for p in progresos if p.estado == 'completada'])
        
        # Mejor puntuación
        mejor = db.session.query(
            func.max(Progreso.puntuacion)
        ).filter_by(
            parada_id=parada_id,
            estado='completada'
        ).scalar() or 0
        
        # Tiempo promedio de completado
        tiempo_promedio = db.session.query(
            func.avg(Progreso.tiempo_empleado)
        ).filter_by(
            parada_id=parada_id,
            estado='completada'
        ).scalar() or 0
        
        return jsonify({
            'parada': parada.to_dict(),
            'estadisticas': {
                'usuarios_completaron': completados,
                'mejor_puntuacion': mejor,
                'tiempo_promedio_segundos': round(tiempo_promedio, 2)
            },
            'detalles_intentos': intentos_stats,
            'fecha_consulta': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/sesiones', methods=['GET'])
def listar_sesiones():
    """
    Lista sesiones con filtros.
    
    Query params:
        - usuario_id: Filtrar por usuario
        - estado: activa, cerrada, expirada
        - desde: Fecha inicio
        - hasta: Fecha fin
        - limite: Máximo resultados
        - pagina: Página actual
    """
    from ..models import Sesion, EstadoSesion
    
    try:
        # Obtener parámetros
        usuario_id = request.args.get('usuario_id', type=int)
        estado = request.args.get('estado')
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        limite = request.args.get('limite', 50, type=int)
        pagina = request.args.get('pagina', 1, type=int)
        
        # Construir query
        query = Sesion.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if estado:
            try:
                estado_enum = EstadoSesion(estado)
                query = query.filter_by(estado=estado_enum)
            except ValueError:
                pass
        
        if desde:
            try:
                fecha_desde = datetime.fromisoformat(desde)
                query = query.filter(Sesion.fecha_inicio >= fecha_desde)
            except:
                pass
        
        if hasta:
            try:
                fecha_hasta = datetime.fromisoformat(hasta)
                query = query.filter(Sesion.fecha_inicio <= fecha_hasta)
            except:
                pass
        
        # Ordenar y paginar
        query = query.order_by(Sesion.fecha_inicio.desc())
        total = query.count()
        
        offset = (pagina - 1) * limite
        sesiones = query.offset(offset).limit(limite).all()
        
        return jsonify({
            'sesiones': [s.to_dict() for s in sesiones],
            'paginacion': {
                'pagina': pagina,
                'limite': limite,
                'total': total,
                'paginas_totales': (total + limite - 1) // limite
            }
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error en listar_sesiones: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'tipo': type(e).__name__}), 500


@estadisticas_api_bp.route('/sesiones', methods=['POST'])
def registrar_sesion():
    """
    Registra una nueva sesión de usuario.
    
    Body JSON:
        - usuario_id: ID del usuario (requerido)
        - tipo_dispositivo: android, ios, web, tablet
        - device_info: Información del dispositivo
    
    Returns:
        Sesión creada
    """
    from ..models import Sesion, TipoDispositivo
    
    try:
        data = request.get_json()
        
        if not data or 'usuario_id' not in data:
            return jsonify({'error': 'usuario_id es requerido'}), 400
        
        # Parsear tipo de dispositivo
        tipo_str = data.get('tipo_dispositivo', 'desconocido')
        try:
            tipo_dispositivo = TipoDispositivo(tipo_str)
        except ValueError:
            tipo_dispositivo = TipoDispositivo.DESCONOCIDO
        
        # Crear sesión
        sesion = Sesion.crear_sesion(
            usuario_id=data['usuario_id'],
            tipo_dispositivo=tipo_dispositivo,
            device_info=data.get('device_info'),
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'mensaje': 'Sesión registrada',
            'sesion': sesion.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/sesiones/<int:sesion_id>/cerrar', methods=['POST'])
def cerrar_sesion(sesion_id: int):
    """
    Cierra una sesión activa.
    
    Args:
        sesion_id: ID de la sesión a cerrar
    """
    from ..models import Sesion
    
    try:
        sesion = Sesion.query.get_or_404(sesion_id)
        sesion.cerrar()
        
        return jsonify({
            'mensaje': 'Sesión cerrada',
            'sesion': sesion.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/intentos', methods=['GET'])
def listar_intentos():
    """
    Lista historial de intentos con filtros.
    
    Query params:
        - usuario_id: Filtrar por usuario
        - parada_id: Filtrar por parada
        - tipo: Tipo de actividad
        - resultado: exito, fallo, abandonado
        - limite: Máximo resultados
    """
    from ..models import HistorialIntento, ResultadoIntento, TipoActividad
    
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        parada_id = request.args.get('parada_id', type=int)
        tipo = request.args.get('tipo')
        resultado = request.args.get('resultado')
        limite = request.args.get('limite', 50, type=int)
        
        query = HistorialIntento.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if parada_id:
            query = query.filter_by(parada_id=parada_id)
        
        if tipo:
            try:
                tipo_enum = TipoActividad(tipo)
                query = query.filter_by(tipo_actividad=tipo_enum)
            except ValueError:
                pass
        
        if resultado:
            try:
                resultado_enum = ResultadoIntento(resultado)
                query = query.filter_by(resultado=resultado_enum)
            except ValueError:
                pass
        
        intentos = query.order_by(
            HistorialIntento.fecha_creacion.desc()
        ).limit(limite).all()
        
        return jsonify({
            'intentos': [i.to_dict() for i in intentos],
            'total': len(intentos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/intentos', methods=['POST'])
def registrar_intento():
    """
    Registra un nuevo intento en una actividad.
    
    Body JSON:
        - usuario_id: ID del usuario (requerido)
        - parada_id: ID de la parada (requerido)
        - tipo_actividad: Tipo de mini-juego
        - puntuacion: Puntuación obtenida (0-100)
        - tiempo_segundos: Tiempo empleado
        - resultado: exito, fallo, abandonado
        - errores: Número de errores
        - pistas_usadas: Pistas utilizadas
    
    Returns:
        Intento registrado
    """
    from ..models import HistorialIntento, TipoActividad, ResultadoIntento
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        # Validar campos requeridos
        if 'usuario_id' not in data or 'parada_id' not in data:
            return jsonify({'error': 'usuario_id y parada_id son requeridos'}), 400
        
        # Parsear enums
        tipo_str = data.get('tipo_actividad', 'otro')
        try:
            tipo = TipoActividad(tipo_str)
        except ValueError:
            tipo = TipoActividad.OTRO
        
        resultado_str = data.get('resultado', 'exito')
        try:
            resultado = ResultadoIntento(resultado_str)
        except ValueError:
            resultado = ResultadoIntento.EXITO
        
        # Registrar intento
        intento = HistorialIntento.registrar_intento(
            usuario_id=data['usuario_id'],
            parada_id=data['parada_id'],
            tipo_actividad=tipo,
            puntuacion=data.get('puntuacion', 0),
            tiempo_segundos=data.get('tiempo_segundos', 0),
            resultado=resultado,
            errores=data.get('errores', 0),
            pistas_usadas=data.get('pistas_usadas', 0),
            detalles=data.get('detalles')
        )
        
        return jsonify({
            'mensaje': 'Intento registrado',
            'intento': intento.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/evolucion/<int:usuario_id>', methods=['GET'])
def evolucion_usuario(usuario_id: int):
    """
    Obtiene la evolución de un usuario (para gráficos).
    
    Args:
        usuario_id: ID del usuario
    
    Query params:
        - parada_id: Filtrar por parada específica
    
    Returns:
        Array de puntos para gráfico de evolución
    """
    from ..models import HistorialIntento
    
    try:
        parada_id = request.args.get('parada_id', type=int)
        
        evolucion = HistorialIntento.get_evolucion_usuario(
            usuario_id=usuario_id,
            parada_id=parada_id
        )
        
        return jsonify({
            'usuario_id': usuario_id,
            'evolucion': evolucion
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@estadisticas_api_bp.route('/ranking', methods=['GET'])
def ranking_usuarios():
    """
    Obtiene el ranking de usuarios por diferentes criterios.
    
    Query params:
        - criterio: puntuacion, paradas, logros, tiempo
        - limite: Máximo resultados
    
    Returns:
        Lista ordenada de usuarios
    """
    from app.models import Usuario, Progreso
    from ..models import LogroUsuario
    from sqlalchemy import func
    from app import db
    
    try:
        criterio = request.args.get('criterio', 'puntuacion')
        limite = request.args.get('limite', 10, type=int)
        
        if criterio == 'puntuacion':
            # Ranking por puntuación total
            ranking = db.session.query(
                Usuario,
                func.sum(Progreso.puntuacion).label('total_puntos')
            ).join(Progreso).filter(
                Progreso.estado == 'completada'
            ).group_by(Usuario.id).order_by(
                func.sum(Progreso.puntuacion).desc()
            ).limit(limite).all()
            
            resultado = [
                {
                    'posicion': i + 1,
                    'usuario': u.to_dict(),
                    'puntuacion_total': int(pts or 0)
                }
                for i, (u, pts) in enumerate(ranking)
            ]
        
        elif criterio == 'paradas':
            # Ranking por paradas completadas
            ranking = db.session.query(
                Usuario,
                func.count(Progreso.id).label('paradas_completadas')
            ).join(Progreso).filter(
                Progreso.estado == 'completada'
            ).group_by(Usuario.id).order_by(
                func.count(Progreso.id).desc()
            ).limit(limite).all()
            
            resultado = [
                {
                    'posicion': i + 1,
                    'usuario': u.to_dict(),
                    'paradas_completadas': int(cnt or 0)
                }
                for i, (u, cnt) in enumerate(ranking)
            ]
        
        elif criterio == 'logros':
            # Ranking por logros desbloqueados
            ranking = db.session.query(
                Usuario,
                func.count(LogroUsuario.id).label('total_logros')
            ).outerjoin(LogroUsuario).filter(
                LogroUsuario.progreso >= 100
            ).group_by(Usuario.id).order_by(
                func.count(LogroUsuario.id).desc()
            ).limit(limite).all()
            
            resultado = [
                {
                    'posicion': i + 1,
                    'usuario': u.to_dict(),
                    'logros_desbloqueados': int(cnt or 0)
                }
                for i, (u, cnt) in enumerate(ranking)
            ]
        
        else:
            return jsonify({'error': 'Criterio no válido'}), 400
        
        return jsonify({
            'criterio': criterio,
            'ranking': resultado
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
