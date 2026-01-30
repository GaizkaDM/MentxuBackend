# ==============================================================================
# 📊 API REST - EXPORTACIÓN DE DATOS
# ==============================================================================

from flask import Blueprint, jsonify, request, Response
from datetime import datetime

exportar_api_bp = Blueprint('exportar_api', __name__, url_prefix='/api/exportar')


@exportar_api_bp.route('/formatos', methods=['GET'])
def formatos_disponibles():
    """Lista los formatos de exportación disponibles."""
    from ..exporters import ExporterFactory
    return jsonify({'formatos': ExporterFactory.get_formatos_disponibles()}), 200


@exportar_api_bp.route('/sesiones', methods=['POST'])
def exportar_sesiones():
    """Exporta datos de sesiones."""
    from ..exporters import ExporterFactory, FiltroExportacion
    from ..models import Sesion
    
    try:
        data = request.get_json() or {}
        formato = data.get('formato', 'csv')
        filtros_data = data.get('filtros', {})
        
        filtros = FiltroExportacion(
            usuario_id=filtros_data.get('usuario_id'),
            fecha_inicio=datetime.fromisoformat(filtros_data['fecha_inicio']) if filtros_data.get('fecha_inicio') else None,
            fecha_fin=datetime.fromisoformat(filtros_data['fecha_fin']) if filtros_data.get('fecha_fin') else None,
            estado=filtros_data.get('estado')
        )
        
        exporter = ExporterFactory.crear_desde_string(formato, "sesiones", filtros)
        contenido = exporter.exportar_modelo(Sesion)
        
        return Response(
            contenido,
            mimetype=exporter.get_content_type(),
            headers={'Content-Disposition': f'attachment; filename={exporter.get_nombre_archivo_completo()}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@exportar_api_bp.route('/intentos', methods=['POST'])
def exportar_intentos():
    """Exporta historial de intentos."""
    from ..exporters import ExporterFactory, FiltroExportacion
    from ..models import HistorialIntento
    
    try:
        data = request.get_json() or {}
        formato = data.get('formato', 'csv')
        filtros_data = data.get('filtros', {})
        
        filtros = FiltroExportacion(
            usuario_id=filtros_data.get('usuario_id'),
            parada_id=filtros_data.get('parada_id')
        )
        
        exporter = ExporterFactory.crear_desde_string(formato, "historial", filtros)
        contenido = exporter.exportar_modelo(HistorialIntento)
        
        return Response(
            contenido,
            mimetype=exporter.get_content_type(),
            headers={'Content-Disposition': f'attachment; filename={exporter.get_nombre_archivo_completo()}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@exportar_api_bp.route('/usuarios', methods=['POST'])
def exportar_usuarios():
    """Exporta datos de usuarios."""
    from ..exporters import ExporterFactory
    from app.models import Usuario
    
    try:
        data = request.get_json() or {}
        formato = data.get('formato', 'csv')
        
        usuarios = Usuario.query.all()
        datos = [u.to_dict() for u in usuarios]
        
        exporter = ExporterFactory.crear_desde_string(formato, "usuarios")
        contenido = exporter.exportar(datos)
        
        return Response(
            contenido,
            mimetype=exporter.get_content_type(),
            headers={'Content-Disposition': f'attachment; filename={exporter.get_nombre_archivo_completo()}'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
