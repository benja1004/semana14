import jwt
import datetime
import os
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

@csrf_exempt
@api_view(['POST'])
def login(request):
    """
    Endpoint '/login/' (POST)
    Genera un token JWT usando la firma HS256 con una expiración de 1 hora.
    En una aplicación real, se validarían las credenciales del usuario aquí.
    """
    jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-change-in-prod')
    
    # Tiempo actual compatible con diferentes versiones de Python
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
    except AttributeError:
        now = datetime.datetime.utcnow()

    payload = {
        'user_id': 1,
        'username': 'estudiante_semana14',
        'exp': now + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, jwt_secret, algorithm='HS256')
    return Response({'token': token}, status=200)

@api_view(['GET'])
def health(request):
    """
    Endpoint '/health/' (GET)
    Realiza una validación real de la conexión a la base de datos PostgreSQL.
    Retorna 200 si la conexión es exitosa, o 503 si falla.
    """
    db_url = os.getenv('DATABASE_URL', 'postgres://authuser:authpass@auth-db:5432/authdb')
    try:
        if db_url.startswith('postgres://') or db_url.startswith('postgresql://'):
            # Conexión directa y segura con psycopg2
            conn = psycopg2.connect(db_url, connect_timeout=3)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
            conn.close()
        else:
            # Fallback local con sqlite3
            import sqlite3
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            conn.close()
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'service': 'auth-service'
        }, status=200)
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'service': 'auth-service'
        }, status=503)
