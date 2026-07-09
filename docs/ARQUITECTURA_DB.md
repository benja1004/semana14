# Arquitectura de Datos y Migraciones (Rol: Sulluchuco — Arquitecto de Microservicios & DB)

Este documento describe el **aislamiento estricto de base de datos (Database-per-Service)** y la
**gestión de migraciones iniciales independientes** de cada microservicio.

---

## 1. Aislamiento estricto: Database-per-Service

Cada microservicio es dueño exclusivo de su base de datos. No existe una base de datos compartida
ni acceso cruzado a tablas: la información que un servicio necesita de otro se resuelve vía el
token JWT o mediante llamadas HTTP inter-servicio, nunca por consultas SQL directas.

| Microservicio     | Base de Datos | Usuario       | Contenedor Postgres | App de dominio | Tabla                 |
| :---------------- | :------------ | :------------ | :------------------ | :------------- | :-------------------- |
| `auth-service`    | `authdb`      | `authuser`    | `auth-db`           | `accounts`     | `auth_user_account`   |
| `catalog-service` | `catalogdb`   | `cataloguser` | `catalog-db`        | `catalog`      | `catalog_product`     |

- Cada `settings.py` construye su `DATABASES['default']` a partir de su propia variable
  `DATABASE_URL` (inyectada por `docker-compose.yml` / ConfigMap-Secret en K8s).
- Credenciales, volúmenes de datos y puertos son **independientes** por servicio
  (`auth-data` y `catalog-data` en Docker; PVC/servicios separados en K8s).

```
auth-service ──> authdb   (auth_user_account)      ✗ sin acceso a catalogdb
catalog-service ──> catalogdb (catalog_product)    ✗ sin acceso a authdb
```

## 2. Modelos de dominio

- `auth-service/accounts/models.py` → `UserAccount` (identidad de usuario; **solo** en `authdb`).
- `catalog-service/catalog/models.py` → `Product` (catálogo; **solo** en `catalogdb`).

Ambas apps están registradas en el `INSTALLED_APPS` de su respectivo servicio, de modo que
`makemigrations` genera migraciones propias y `migrate` crea las tablas en la DB correcta.

## 3. Migraciones iniciales independientes

Los archivos de migración ya están versionados en el repositorio:

- `auth-service/accounts/migrations/0001_initial.py`   → crea `auth_user_account`
- `catalog-service/catalog/migrations/0001_initial.py` → crea `catalog_product`

### Regenerar (si se modifican los modelos)

```bash
# auth-service
cd auth-service && python manage.py makemigrations accounts

# catalog-service
cd catalog-service && python manage.py makemigrations catalog
```

### Aplicar migraciones (Docker Compose)

```bash
docker-compose up -d --build
docker-compose exec auth-service    python manage.py migrate   # -> authdb
docker-compose exec catalog-service python manage.py migrate   # -> catalogdb
```

> En Kubernetes, `migrate` se ejecuta con `kubectl exec <pod> -- python manage.py migrate`
> (o como initContainer/Job de migración, según despliegue del equipo de contenedores).

## 4. Evidencia de verificación (ejecutada localmente contra Postgres real)

`migrate` aplicado correctamente en ambas DBs y aislamiento confirmado:

```text
authdb    -> auth_user_account  presente | catalog_product  AUSENTE (NULL)
catalogdb -> catalog_product    presente | auth_user_account AUSENTE (NULL)
```

Comando de verificación de aislamiento:

```bash
# En authdb NO debe existir la tabla del catálogo (retorna vacío/NULL):
docker-compose exec auth-db    psql -U authuser    -d authdb    -tc "SELECT to_regclass('public.catalog_product');"

# En catalogdb NO debe existir la tabla de usuarios (retorna vacío/NULL):
docker-compose exec catalog-db psql -U cataloguser -d catalogdb -tc "SELECT to_regclass('public.auth_user_account');"
```
