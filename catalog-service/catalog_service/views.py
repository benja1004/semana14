import os
import psycopg2
from rest_framework.decorators import api_view
from rest_framework.response import Response
from catalog_service.utils.client import call_auth_service

@api_view(['GET'])
def catalog_list(request):
    """
    Endpoint '/catalog/' (GET)
    Protegido por el JWTAuthMiddleware.
    Retorna un listado de productos y demuestra la comunicación inter-servicio con auth-service.
    """
    # Obtener el user_id inyectado por el middleware
    user_id = getattr(request, 'user_id', None)
    
    # Propagar cabeceras recibidas (para tracing y tokens) hacia el microservicio auth-service
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    if 'X-Request-ID' in request.headers:
        headers['X-Request-ID'] = request.headers['X-Request-ID']

    # Llamada de resiliencia al microservicio de autenticación (/health/)
    auth_response = call_auth_service('/health/', headers=headers)
    
    # Simulación de catálogo de productos
    products = [
        {'id': 101, 'name': 'Laptop ASUS ZenBook', 'price': 1200.00, 'stock': 15},
        {'id': 102, 'name': 'Teclado Mecánico Keychron K2', 'price': 99.99, 'stock': 30},
        {'id': 103, 'name': 'Audífonos Sony WH-1000XM4', 'price': 280.00, 'stock': 8}
    ]
    
    # Determinar si la llamada inter-servicio fue exitosa
    auth_status = "ok" if auth_response.status_code == 200 else "failed"
    
    return Response({
        'message': 'Catálogo obtenido exitosamente.',
        'user_id': user_id,
        'inter_service_call': {
            'target': 'auth-service/health/',
            'status': auth_status,
            'http_code': auth_response.status_code,
            'x_request_id': auth_response.headers.get('X-Request-ID') or headers.get('X-Request-ID')
        },
        'products': products
    }, status=200)

@api_view(['GET'])
def health(request):
    """
    Endpoint '/health/' (GET)
    Valida la conexión real a PostgreSQL del servicio de catálogo.
    Retorna 200 si la conexión es correcta, o 503 si falla.
    """
    db_url = os.getenv('DATABASE_URL', 'postgres://cataloguser:catalogpass@catalog-db:5432/catalogdb')
    try:
        # Validación con psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=3)
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
        conn.close()
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'service': 'catalog-service'
        }, status=200)
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'service': 'catalog-service'
        }, status=503)
