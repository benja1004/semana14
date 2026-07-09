import subprocess
import time
import requests
import sys
import os

def main():
    print("======================================================================")
    print("Iniciando prueba de integración local de Microservicios (Estilo SQLite)")
    print("======================================================================")

    # Copiar variables de entorno actuales y agregar las necesarias para la prueba
    env_auth = os.environ.copy()
    env_auth["DATABASE_URL"] = "sqlite://"
    env_auth["JWT_SECRET"] = "dev-secret-change-in-prod"
    env_auth["PYTHONPATH"] = "auth-service"

    env_catalog = os.environ.copy()
    env_catalog["DATABASE_URL"] = "sqlite://"
    env_catalog["AUTH_SERVICE_URL"] = "http://127.0.0.1:8001"
    env_catalog["JWT_SECRET"] = "dev-secret-change-in-prod"
    env_catalog["PYTHONPATH"] = "catalog-service"

    # Lanzar auth-service en el puerto 8001
    print("\n[+] Iniciando auth-service en el puerto 8001...")
    auth_process = subprocess.Popen(
        [sys.executable, "auth-service/manage.py", "runserver", "127.0.0.1:8001"],
        env=env_auth,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Lanzar catalog-service en el puerto 8002
    print("[+] Iniciando catalog-service en el puerto 8002...")
    catalog_process = subprocess.Popen(
        [sys.executable, "catalog-service/manage.py", "runserver", "127.0.0.1:8002"],
        env=env_catalog,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Esperar a que los servidores se inicialicen
    time.sleep(3)

    try:
        # 1. Verificar el Health de Auth Service
        print("\n--- Test 1: Healthcheck de Auth Service (/health/) ---")
        res_auth_health = requests.get("http://127.0.0.1:8001/health/")
        print(f"Status Code: {res_auth_health.status_code}")
        print(f"Response: {res_auth_health.json()}")

        # 2. Verificar el Health de Catalog Service
        print("\n--- Test 2: Healthcheck de Catalog Service (/health/) ---")
        res_catalog_health = requests.get("http://127.0.0.1:8002/health/")
        print(f"Status Code: {res_catalog_health.status_code}")
        print(f"Response: {res_catalog_health.json()}")

        # 3. Consumir catálogo sin cabecera de autenticación (401 Esperado)
        print("\n--- Test 3: Consumo de Catálogo sin Token (401 Esperado) ---")
        res_cat_no_token = requests.get("http://127.0.0.1:8002/catalog/")
        print(f"Status Code: {res_cat_no_token.status_code}")
        print(f"Response: {res_cat_no_token.json()}")

        # 4. Obtener token JWT de auth-service
        print("\n--- Test 4: Obtención de Token JWT (/login/) ---")
        res_login = requests.post("http://127.0.0.1:8001/login/")
        print(f"Status Code: {res_login.status_code}")
        token_data = res_login.json()
        print(f"Response: {token_data}")
        token = token_data.get("token")

        if not token:
            print("[-] Error: No se pudo obtener el token JWT.")
            return

        # 5. Consumir catálogo con token inválido (403 Esperado)
        print("\n--- Test 5: Consumo de Catálogo con Token Inválido (403 Esperado) ---")
        headers_invalid = {"Authorization": "Bearer token-invalido-12345"}
        res_cat_invalid = requests.get("http://127.0.0.1:8002/catalog/", headers=headers_invalid)
        print(f"Status Code: {res_cat_invalid.status_code}")
        print(f"Response: {res_cat_invalid.json()}")

        # 6. Consumir catálogo con token válido (200 Esperado)
        print("\n--- Test 6: Consumo de Catálogo con Token Válido (200 Esperado) ---")
        headers_valid = {
            "Authorization": f"Bearer {token}",
            "X-Request-ID": "test-trazabilidad-navarro-777"
        }
        res_cat_valid = requests.get("http://127.0.0.1:8002/catalog/", headers=headers_valid)
        print(f"Status Code: {res_cat_valid.status_code}")
        print(f"Response: {res_cat_valid.json()}")

    except Exception as e:
        print(f"\n[-] Ocurrió un error durante la ejecución de las pruebas: {e}")
    finally:
        # Terminar procesos de los servidores
        print("\n[+] Cerrando servidores de desarrollo...")
        auth_process.terminate()
        catalog_process.terminate()
        try:
            auth_process.wait(timeout=2)
            catalog_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            auth_process.kill()
            catalog_process.kill()
        print("[+] Servidores cerrados exitosamente.")

if __name__ == "__main__":
    main()
