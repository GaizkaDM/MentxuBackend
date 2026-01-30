# ==============================================================================
# 📊 DASHBOARD WEB - Rutas para el panel de estadísticas
# ==============================================================================

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta

dashboard_bp = Blueprint(
    'dashboard_estadisticas', 
    __name__,
    template_folder='../templates',
    url_prefix='/dashboard'
)


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal de estadísticas."""
    from app.models import Usuario, Parada, Progreso
    from ..models import Sesion, HistorialIntento, LogroUsuario
    from sqlalchemy import func
    from app import db
    
    # Estadísticas básicas
    stats = {
        'usuarios': Usuario.query.count(),
        'sesiones_hoy': Sesion.query.filter(
            func.date(Sesion.fecha_inicio) == datetime.utcnow().date()
        ).count(),
        'paradas_completadas': Progreso.query.filter_by(estado='completada').count(),
        'logros_desbloqueados': LogroUsuario.query.filter(
            LogroUsuario.progreso >= 100
        ).count()
    }
    
    # Datos para gráficos
    ultimos_7_dias = []
    for i in range(6, -1, -1):
        fecha = datetime.utcnow().date() - timedelta(days=i)
        sesiones = Sesion.query.filter(
            func.date(Sesion.fecha_inicio) == fecha
        ).count()
        ultimos_7_dias.append({
            'fecha': fecha.strftime('%d/%m'),
            'sesiones': sesiones
        })
    
    # Usuarios recientes
    usuarios_recientes = Usuario.query.order_by(
        Usuario.fecha_registro.desc()
    ).limit(5).all()
    
    return render_template(
        'estadisticas/dashboard.html',
        stats=stats,
        ultimos_7_dias=ultimos_7_dias,
        usuarios_recientes=usuarios_recientes
    )


@dashboard_bp.route('/usuarios')
@login_required
def usuarios():
    """Vista de estadísticas de usuarios."""
    from app.models import Usuario, Progreso
    from ..models import LogroUsuario
    from sqlalchemy import func
    from app import db
    
    pagina = request.args.get('pagina', 1, type=int)
    limite = 20
    
    usuarios_query = Usuario.query.order_by(Usuario.fecha_registro.desc())
    total = usuarios_query.count()
    
    usuarios = usuarios_query.offset((pagina-1)*limite).limit(limite).all()
    
    # Enriquecer con estadísticas
    usuarios_data = []
    for u in usuarios:
        paradas = Progreso.query.filter_by(
            usuario_id=u.id, estado='completada'
        ).count()
        logros = LogroUsuario.query.filter(
            LogroUsuario.usuario_id == u.id,
            LogroUsuario.progreso >= 100
        ).count()
        
        usuarios_data.append({
            'usuario': u,
            'paradas_completadas': paradas,
            'logros': logros
        })
    
    return render_template(
        'estadisticas/usuarios.html',
        usuarios=usuarios_data,
        pagina=pagina,
        total_paginas=(total + limite - 1) // limite
    )


@dashboard_bp.route('/actividades')
@login_required
def actividades():
    """Vista de estadísticas de actividades."""
    from app.models import Parada
    from ..models import HistorialIntento
    from sqlalchemy import func
    from app import db
    
    paradas = Parada.query.order_by(Parada.orden).all()
    
    paradas_data = []
    for p in paradas:
        stats = HistorialIntento.get_estadisticas_parada(p.id)
        paradas_data.append({
            'parada': p,
            'estadisticas': stats
        })
    
    return render_template(
        'estadisticas/actividades.html',
        paradas=paradas_data
    )


@dashboard_bp.route('/exportar')
@login_required
def exportar():
    """Vista para exportar datos."""
    return render_template('estadisticas/exportar.html')


@dashboard_bp.route('/api/grafico/sesiones')
@login_required
def api_grafico_sesiones():
    """API para datos del gráfico de sesiones."""
    from ..models import Sesion
    from sqlalchemy import func
    from app import db
    
    dias = request.args.get('dias', 7, type=int)
    
    datos = []
    for i in range(dias-1, -1, -1):
        fecha = datetime.utcnow().date() - timedelta(days=i)
        count = Sesion.query.filter(
            func.date(Sesion.fecha_inicio) == fecha
        ).count()
        datos.append({
            'fecha': fecha.strftime('%Y-%m-%d'),
            'label': fecha.strftime('%d %b'),
            'valor': count
        })
    
    return jsonify({'datos': datos})


@dashboard_bp.route('/api/grafico/actividades')
@login_required
def api_grafico_actividades():
    """API para datos del gráfico de actividades."""
    from app.models import Parada, Progreso
    from sqlalchemy import func
    from app import db
    
    datos = db.session.query(
        Parada.nombre_corto,
        func.count(Progreso.id).label('completadas')
    ).outerjoin(Progreso, Progreso.parada_id == Parada.id).filter(
        Progreso.estado == 'completada'
    ).group_by(Parada.id).order_by(Parada.orden).all()
    
    return jsonify({
        'labels': [d[0] for d in datos],
        'valores': [d[1] for d in datos]
    })
