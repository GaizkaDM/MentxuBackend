from flask import Blueprint, render_template, current_app, request
from flask_login import login_required
from app import db
from app.models import Usuario, Parada, Progreso
from sqlalchemy import func

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    """Página principal (pública)"""
    total_usuarios = Usuario.query.count()
    total_paradas = Parada.query.count()
    total_completados = Progreso.query.filter_by(estado='completada').count()
    
    return render_template('index.html',
                         total_usuarios=total_usuarios,
                         total_paradas=total_paradas,
                         total_completados=total_completados)


@web_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de control principal (requiere login)"""
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_usuarios = Usuario.query.count()
    total_paradas = Parada.query.count()
    progreso_completado = Progreso.query.filter_by(estado='completada').count()
    progreso_activo = Progreso.query.filter_by(estado='activa').count()
    
    # Usuarios recientes
    usuarios_recientes = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(10).all()
    
    # Estadísticas por parada
    stats_paradas = db.session.query(
        Parada.nombre_corto,
        func.count(Progreso.id).label('total_completados')
    ).join(Progreso).filter(
        Progreso.estado == 'completada'
    ).group_by(Parada.id).all()
    
    # ========== ESTADÍSTICAS AVANZADAS ==========
    sesiones_hoy = 0
    logros_desbloqueados = 0
    total_intentos = 0
    ultimos_7_dias = []
    
    try:
        from app.estadisticas.models import Sesion, LogroUsuario, HistorialIntento
        
        # Sesiones de hoy
        sesiones_hoy = Sesion.query.filter(
            func.date(Sesion.fecha_inicio) == datetime.utcnow().date()
        ).count()
        
        # Total logros desbloqueados
        logros_desbloqueados = LogroUsuario.query.filter(
            LogroUsuario.progreso >= 100
        ).count()
        
        # Total intentos
        total_intentos = HistorialIntento.query.count()
        
        # Sesiones últimos 7 días (para gráfico)
        for i in range(6, -1, -1):
            fecha = datetime.utcnow().date() - timedelta(days=i)
            count = Sesion.query.filter(
                func.date(Sesion.fecha_inicio) == fecha
            ).count()
            ultimos_7_dias.append({
                'fecha': fecha.strftime('%d/%m'),
                'sesiones': count
            })
    except ImportError:
        # Módulo de estadísticas no disponible
        for i in range(7):
            ultimos_7_dias.append({'fecha': '', 'sesiones': 0})
    
    return render_template('dashboard.html',
                         total_usuarios=total_usuarios,
                         total_paradas=total_paradas,
                         progreso_completado=progreso_completado,
                         progreso_activo=progreso_activo,
                         usuarios_recientes=usuarios_recientes,
                         stats_paradas=stats_paradas,
                         # Nuevas estadísticas
                         sesiones_hoy=sesiones_hoy,
                         logros_desbloqueados=logros_desbloqueados,
                         total_intentos=total_intentos,
                         ultimos_7_dias=ultimos_7_dias)


@web_bp.route('/mapa')
@login_required
def mapa():
    """Mapa interactivo con todas las paradas"""
    paradas = Parada.query.order_by(Parada.orden).all()
    mapbox_token = current_app.config.get('MAPBOX_ACCESS_TOKEN', '')
    paradas_json = [p.to_dict() for p in paradas]
    
    return render_template('mapa.html', paradas=paradas, mapbox_token=mapbox_token, paradas_json=paradas_json)


@web_bp.route('/usuarios')
@login_required
def usuarios():
    """Lista de todos los usuarios"""
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('usuarios.html', usuarios=usuarios)


@web_bp.route('/usuarios/<int:id>')
@login_required
def usuario_detalle(id):
    """Detalle de un usuario específico con su progreso"""
    usuario = Usuario.query.get_or_404(id)
    progresos = Progreso.query.filter_by(usuario_id=id).join(Parada).order_by(Parada.orden).all()
    
    return render_template('usuario_detalle.html', usuario=usuario, progresos=progresos)


@web_bp.route('/admin')
@login_required
def admin():
    """Panel de administración para gestionar paradas"""
    paradas = Parada.query.order_by(Parada.orden).all()
    return render_template('admin.html', paradas=paradas)


@web_bp.route('/ranking')
@login_required
def ranking():
    """Ranking de alumnos por puntuación total"""
    ranking_data = db.session.query(
        Usuario.id,
        Usuario.nombre,
        Usuario.apellido,
        func.sum(Progreso.puntuacion).label('puntuacion_total'),
        func.count(Progreso.id).label('paradas_completadas')
    ).join(Progreso).filter(Progreso.estado == 'completada')\
     .group_by(Usuario.id, Usuario.nombre, Usuario.apellido)\
     .order_by(func.sum(Progreso.puntuacion).desc())\
     .all()
    
    return render_template('ranking.html', ranking=ranking_data)
