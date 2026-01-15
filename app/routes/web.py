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
    
    return render_template('dashboard.html',
                         total_usuarios=total_usuarios,
                         total_paradas=total_paradas,
                         progreso_completado=progreso_completado,
                         progreso_activo=progreso_activo,
                         usuarios_recientes=usuarios_recientes,
                         stats_paradas=stats_paradas)


@web_bp.route('/mapa')
@login_required
def mapa():
    """Mapa interactivo con todas las paradas"""
    paradas = Parada.query.order_by(Parada.orden).all()
    api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('mapa.html', paradas=paradas, api_key=api_key)


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
