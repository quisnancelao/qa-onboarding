# Evaluación QA: Onboarding Digital

Proyecto de pruebas con una API local simulada, un flujo web de compra en SauceDemo y una prueba de carga local con JMeter.

## Requisitos

- Python 3.13 o 3.14
- Git
- JMeter y Java para la prueba de carga

## Instalación

Desde PowerShell, en la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Pruebas automatizadas

```powershell
.\.venv\Scripts\python.exe -m pytest tests/api tests/transactional -v
.\.venv\Scripts\python.exe -m pytest tests/web -v
```

Las pruebas de API cubren creación y consulta de tracking y casos negativos. Las pruebas transaccionales comprueban que una notificación de pago repetida no duplique la operación y que una clave de idempotencia no se reutilice para otro tracking.

La prueba web recorre una compra simulada en [SauceDemo](https://www.saucedemo.com/) y guarda una captura en `evidencias/compra_saucedemo.png`.

## Prueba de carga local

Primero, iniciar la API desde la raíz del proyecto y dejar esa terminal abierta:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Luego, ejecutar `tests/load/tracking_load.jmx` con JMeter en modo consola. El plan envía 50 solicitudes de creación de tracking a `127.0.0.1:8000` y comprueba que respondan con HTTP 201.

Resultados de la ejecución registrada en `evidencias/carga_resultados.jtl`: 50 solicitudes, 0 errores y 9 ms de tiempo promedio. Son resultados del simulador ejecutado localmente; pueden variar según el equipo.

## Estructura

- `app/`: API local simulada con datos en memoria.
- `tests/api/`: pruebas positivas y negativas de tracking.
- `tests/transactional/`: pruebas de idempotencia de pagos.
- `tests/async_tests/`: pruebas de reintentos, pagos duplicados y consulta de trabajos.
- `pages/`: Page Object de SauceDemo.
- `tests/web/`: prueba de compra simulada.
- `tests/load/tracking_load.jmx`: plan de JMeter.
- `evidencias/`: captura web y resultados de carga.

## Pendiente
Configuración del pipeline de CI.