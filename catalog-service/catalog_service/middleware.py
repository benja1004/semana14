import jwt
import os
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware para validar autenticación JWT en las solicitudes entrantes.
    Excluye las rutas de administración (/admin/) y healthchecks (/health/).
    """
    def process_request(self, request):
        # Excluir de autenticación las rutas críticas
        if request.path.startswith('/admin/') or request.path == '/health/':
            return None

        # Obtener cabecera de autorización de headers modernos o META clásico
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Token missing',
                'message': 'Se requiere cabecera de autorización formateada como: Bearer <token>'
            }, status=401)

        try:
            parts = auth_header.split(' ')
            if len(parts) != 2:
                return JsonResponse({'error': 'Invalid token format', 'message': 'El token debe ser Bearer <token>'}, status=401)
            
            token = parts[1]
            jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-change-in-prod')
            
            # Decodificar el token con el secreto inyectado por entorno
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            
            # Inyectar el user_id decodificado directamente en la solicitud
            request.user_id = payload.get('user_id')
            
            return None # Permite que Django prosiga con la vista
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                'error': 'Token expired',
                'message': 'El token JWT ha expirado. Por favor, solicite uno nuevo.'
            }, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                'error': 'Invalid token',
                'message': 'El token provisto es inválido o la firma no coincide.'
            }, status=403)
        except Exception as e:
            return JsonResponse({
                'error': 'Authentication error',
                'message': str(e)
            }, status=500)
