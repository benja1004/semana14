import requests
import os
import uuid
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Crear e inicializar una sesión global para reutilización de conexiones (Keep-Alive)
session = requests.Session()

# Configurar estrategia de reintentos resiliente con backoff exponencial
# Reintenta un máximo de 3 veces si encuentra errores 500, 502, 503 o 504.
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,  # Tiempos de espera: 0.5s, 1.0s, 2.0s
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

def call_auth_service(endpoint: str, headers: dict = None) -> requests.Response:
    """
    Realiza llamadas al servicio de autenticación (`auth-service`) usando la sesión configurada.
    Propaga y genera 'X-Request-ID' para trazabilidad (tracing).
    Aplica un timeout estricto de 3 segundos.
    """
    base_url = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8000')
    # Limpiar barras diagonales para evitar URLs mal formadas
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    # Clonar cabeceras para no modificar la referencia original
    headers = headers.copy() if headers else {}
    
    # Asegurar la generación y propagación del header de trazabilidad
    if 'X-Request-ID' not in headers:
        headers['X-Request-ID'] = str(uuid.uuid4())
        
    try:
        # Petición GET con timeout de 3 segundos
        response = session.get(url, headers=headers, timeout=3)
        return response
    except requests.exceptions.Timeout as e:
        # Estructurar respuesta simulada de error de timeout (Gateway Timeout)
        mock_response = requests.Response()
        mock_response.status_code = 504
        mock_response._content = b'{"error": "Timeout calling auth-service", "details": "' + str(e).encode('utf-8') + b'"}'
        return mock_response
    except requests.exceptions.RequestException as e:
        # Captura de errores genéricos de conexión (Service Unavailable)
        mock_response = requests.Response()
        mock_response.status_code = 503
        mock_response._content = b'{"error": "Connection error calling auth-service", "details": "' + str(e).encode('utf-8') + b'"}'
        return mock_response
