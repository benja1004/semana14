# Guía de Trabajo y Reparto Colaborativo - Semana 14
## Asignación de Roles y Tareas del Ecosistema de Microservicios

Para maximizar el aprendizaje y cumplir con los criterios de evaluación de la Rúbrica, se ha estructurado el trabajo del equipo (Sulluchuco, Toribio, Navarro, Batja, Yauri) de la siguiente manera:

---

### 1. Cuadro de Roles y Responsabilidades

| Integrante | Rol Técnico | Tareas Específicas en este Repositorio |
| :--- | :--- | :--- |
| **Sulluchuco** | **Arquitecto de Microservicios & DB** | - Aislamiento estricto de base de datos (Database-per-Service).<br>- Gestión de migraciones iniciales de django (`makemigrations`, `migrate`) independientes en sus respectivas DBs (authdb y catalogdb). |
| **Toribio** | **Ingeniero de Contenedores & K8s** | - Mantener y optimizar los `Dockerfile` multi-stage securizados (Non-Root, usuario `appuser`).<br>- Mantener el `docker-compose.yml` para el desarrollo local.<br>- Configurar y validar la aplicación de los manifiestos en Kubernetes (`deployment`, `service`, `ingress`, `configmap`, `secret`). |
| **Navarro** | **Especialista en Comunicación & Seguridad** | - Lógica de generación de firmas JWT en `auth-service/views.py`.<br>- Implementación del `JWTAuthMiddleware` para decodificar y validar tokens en el `catalog-service`.<br>- Configuración del cliente HTTP inter-servicio resiliente con reintentos y backoff. |
| **Batja** | **QA de Observabilidad & Escalado** | - Pruebas y validación del endpoint `/health/` con conexión real a Postgres.<br>- Configurar y verificar la respuesta a nivel K8s de las `readinessProbe` y `livenessProbe`.<br>- Ejecutar la prueba de escalado horizontal (`kubectl scale --replicas=3`) y monitorear los pods. |
| **Yauri** | **Integrador de APIs y Consumo** | - Integrar los flujos de consumo de las APIs `/login/` y `/catalog/`.<br>- Crear scripts de validación con cURL o colección de Postman.<br>- Consolidar y verificar las respuestas HTTP (401, 403, 503) e inyectar tracing. |

---

### 2. Flujo de Git y Ramas de Trabajo

Cada integrante trabajará en su propia rama de desarrollo para evitar conflictos y emular un entorno de producción real.

#### Pasos para Trabajar en tu Rama:

1. **Clonar el repositorio y descargar cambios:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd semana14
   ```

2. **Cambiarse a su rama asignada:**
   * Sulluchuco: `git checkout dev-sulluchuco`
   * Toribio: `git checkout dev-toribio`
   * Navarro: `git checkout dev-navarro`
   * Batja: `git checkout dev-batja`
   * Yauri: `git checkout dev-yauri`

3. **Realizar cambios y subirlos:**
   ```bash
   git add .
   git commit -m "feat(rol): descripción de tu aporte o prueba ejecutada"
   git push origin dev-<tu-apellido>
   ```

4. **Integración (Pull Request):**
   Una vez completadas y testeadas localmente las tareas de su rol, abran un PR hacia la rama `main` para consolidar el laboratorio.

---

### 3. Instrucciones de Ejecución y Pruebas Locales

#### Fase A: Desarrollo y Ejecución con Docker Compose
1. **Crear archivo de entorno local:**
   Copie el archivo de ejemplo para levantar los servicios localmente:
   ```bash
   cp .env.example .env
   ```
2. **Levantar el ecosistema completo:**
   ```bash
   docker-compose up --build
   ```
3. **Ejecutar migraciones en los contenedores levantados:**
   ```bash
   # Migraciones para auth-service
   docker-compose exec auth-service python manage.py migrate
   
   # Migraciones para catalog-service
   docker-compose exec catalog-service python manage.py migrate
   ```
4. **Verificar estado de salud local:**
   - Auth Service Health: [http://localhost:8001/health/](http://localhost:8001/health/)
   - Catalog Service Health: [http://localhost:8002/health/](http://localhost:8002/health/)

#### Fase B: Orquestación en Kubernetes (Minikube / k3s)
1. **Arrancar Minikube e iniciar Ingress addon:**
   ```bash
   minikube start
   minikube addons enable ingress
   ```
2. **Configurar docker env de Minikube (para construir localmente dentro del nodo):**
   ```bash
   # En Windows Powershell:
   minikube docker-env | Invoke-Expression
   ```
3. **Construir las imágenes dentro del entorno minikube:**
   ```bash
   docker build -t auth-service:latest ./auth-service
   docker build -t catalog-service:latest ./catalog-service
   ```
4. **Aplicar los manifiestos de Kubernetes:**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/deployment-auth.yaml
   kubectl apply -f k8s/deployment-catalog.yaml
   kubectl apply -f k8s/service-auth.yaml
   kubectl apply -f k8s/service-catalog.yaml
   kubectl apply -f k8s/ingress.yaml
   ```
5. **Obtener la IP del Ingress:**
   ```bash
   kubectl get ingress
   ```
   Agregue la IP devuelta al archivo `/etc/hosts` (o `C:\Windows\System32\drivers\etc\hosts` en Windows) apuntando a `microservices.local` si prefiere usar hosts virtuales, o consuma directamente mediante la IP obtenida.

---

### 4. Guía de Validación del Flujo (Por Yauri)

1. **Obtener Token JWT de autenticación:**
   ```bash
   curl -X POST http://localhost:8001/login/
   ```
   *Respuesta esperada:*
   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

2. **Consumir el Catálogo Protegido sin Token (Error Esperado 401):**
   ```bash
   curl -X GET http://localhost:8002/catalog/
   ```
   *Respuesta esperada:*
   ```json
   {
     "error": "Token missing",
     "message": "Se requiere cabecera de autorización formateada como: Bearer <token>"
   }
   ```

3. **Consumir el Catálogo Protegido con Token Válido (Éxito 200):**
   ```bash
   curl -X GET http://localhost:8002/catalog/ \
     -H "Authorization: Bearer <PEGAR_TOKEN_AQUÍ>" \
     -H "X-Request-ID: test-custom-tracing-id-12345"
   ```
   *Respuesta esperada:* Muestra los productos y valida que la llamada interna a `auth-service/health/` funcionó propagando el `X-Request-ID`.
