#  Onboarding Digital


## Requisitos

- Python 3.13
- Git
- Chromium para las pruebas web
- Java y Apache JMeter 5.6.3 para ejecutar la prueba de carga

## Instalación en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Pruebas automatizadas

Ejecutar las pruebas de API, pagos, trabajos asíncronos y web:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/api tests/transactional tests/async_tests tests/web -v
```

Las pruebas de API usan una aplicación independiente en memoria. La prueba web automatiza un flujo de compra simulado en SauceDemo mediante Playwright y Page Object Model.

## Ejecutar la API local

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La documentación interactiva estará disponible en http://127.0.0.1:8000/docs. Para detener el servidor, presiona `Ctrl + C`.

## Prueba de carga con JMeter

Con la API local ejecutándose, abre `tests/load/tracking_load.jmx` en JMeter y ejecuta el plan. El plan envía solicitudes de creación de tracking y comprueba que la respuesta sea HTTP 201.

También se puede ejecutar JMeter en modo no gráfico desde su carpeta `bin`:

```powershell
.\jmeter.bat -n -t "C:\Users\Oscar Quisnancela\Desktop\qa-onboarding\tests\load\tracking_load.jmx" -l "C:\Users\Oscar Quisnancela\Desktop\qa-onboarding\evidencias\carga_resultados.jtl"
```

En la ejecución local registrada en `evidencias/carga_resultados.jtl` se completaron 50 solicitudes, con 0 errores y un tiempo promedio aproximado de 9 ms. Estos resultados corresponden al simulador local y pueden variar según el equipo.

## Integración continua

El archivo `.github/workflows/qa.yml` configura GitHub Actions para instalar las dependencias, preparar Chromium y ejecutar las pruebas automatizadas en eventos `push` y `pull_request`. El pipeline **Pruebas QA** se ejecutó correctamente en la rama `main`.

La prueba de JMeter se ejecuta por separado y no forma parte del pipeline.

## Estructura

- `app/`: API simulada local.
- `tests/api/`: pruebas positivas y negativas de tracking.
- `tests/transactional/`: pruebas de idempotencia de pagos.
- `tests/async_tests/`: pruebas de reintentos y trabajos de pago.
- `pages/`: Page Object de SauceDemo.
- `tests/web/`: prueba automatizada de compra.
- `tests/load/tracking_load.jmx`: plan de carga de JMeter.
- `evidencias/`: captura de la compra y resultados de carga.
- `.github/workflows/qa.yml`: pipeline de GitHub Actions.