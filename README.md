# Onboarding Digital 

Repositorio semilla para demostrar una estrategia de automatización aplicada a un flujo de Onboarding Digital.

El proyecto incluye pruebas de API, validación transaccional de idempotencia, procesamiento asíncrono, automatización web, una prueba de carga local y un pipeline de integración continua.

## Requisitos

- Python 3.13
- Git
- Chromium para las pruebas web
- Java 21
- Apache JMeter 5.6.3
- Conexión a Internet únicamente para la prueba web de SauceDemo

## Instalación en Windows

Desde PowerShell, ubicarse en la carpeta principal del proyecto:

```powershell
cd "$env:USERPROFILE\Desktop\qa-onboarding"
```

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Instalar las dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Instalar Chromium para Playwright:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Variables de entorno

El archivo `.env.example` contiene ejemplos de configuración y no almacena datos sensibles.

La prueba web acepta las siguientes variables opcionales:

```powershell
$env:SAUCE_USER="standard_user"
$env:SAUCE_PASSWORD="secret_sauce"
```

Estas credenciales pertenecen a la aplicación pública de práctica SauceDemo. Si no se configuran, la prueba utiliza esos mismos valores públicos como configuración predeterminada.


## Comandos de ejecución

Todos los comandos deben ejecutarse desde la carpeta principal del proyecto.

### Pruebas de API

Ejecuta las pruebas positivas y negativas de creación y consulta de tracking:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/api -v
```

### Pruebas transaccionales

Ejecuta la validación de pagos duplicados, idempotencia y descuento único de inventario:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/transactional -v
```

### Pruebas de procesamiento asíncrono

Ejecuta las validaciones de trabajos en segundo plano, reintentos y mensajes duplicados:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/async_tests -v
```

### Prueba web

Ejecuta el flujo de compra automatizado en SauceDemo:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/web -v
```

Esta prueba requiere conexión a Internet.

### Ejecución completa

Ejecuta las pruebas de API, transaccionales, asíncronas y web:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/api tests/transactional tests/async_tests tests/web -v
```

## Ejecutar la API local

La API local es un simulador desarrollado con FastAPI y utiliza datos almacenados temporalmente en memoria.

Para iniciarla:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La documentación interactiva estará disponible en:

```text
http://127.0.0.1:8000/docs
```

Para detener la API, presiona `Ctrl + C`.

## Prueba de carga con JMeter

La prueba de carga se ejecuta únicamente contra la API local. No se realizan pruebas de carga contra SauceDemo, ReqRes ni otros servicios públicos.

### 1. Iniciar la API

Desde la carpeta principal del proyecto:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Mantén abierta esta terminal.

### 2. Ejecutar JMeter

Abre otra terminal, ingresa a la carpeta `bin` de JMeter y ejecuta:

```cmd
jmeter.bat -n -t "%USERPROFILE%\Desktop\qa-onboarding\tests\load\tracking_load.jmx" -l "%USERPROFILE%\Desktop\qa-onboarding\evidencias\carga_resultados.jtl"
```

El plan ejecuta:

- 10 usuarios virtuales.
- Una rampa de 10 segundos.
- 5 solicitudes por usuario.
- 50 solicitudes en total.
- Validación del código HTTP 201.

En la ejecución registrada en `evidencias/carga_resultados.jtl` se completaron 50 solicitudes, sin errores y con un tiempo promedio aproximado de 9 ms.

Estos resultados pertenecen al simulador ejecutado localmente y pueden variar según las características del equipo.

## Pruebas de API

Las pruebas de API utilizan una aplicación independiente en memoria y validan:

- Creación correcta de un tracking.
- Consulta del tracking creado.
- Rechazo de solicitudes sin el nombre del comercio.
- Respuesta HTTP 404 al consultar un tracking inexistente.
- Código de respuesta y contenido del cuerpo recibido.

No se utilizó ReqRes porque el documento permite utilizar mocks, simuladores o aplicaciones públicas. Se eligió una API local para representar mejor las operaciones del dominio y evitar que la suite dependa de servicios externos.

## Prueba transaccional e idempotencia

La prueba transaccional simula la recepción de dos notificaciones idénticas de pago con la misma clave de idempotencia.

La validación comprueba que:

- La primera notificación procesa el pago.
- La segunda notificación se identifica como duplicada.
- Se registra una sola operación lógica de pago.
- El inventario se descuenta una sola vez.
- El tracking termina en estado `PAID`.
- Una misma clave no puede utilizarse para otro tracking.

## Procesamiento asíncrono

Las pruebas asíncronas simulan trabajos de pago ejecutados en segundo plano.

Se valida:

- El cambio de estado del trabajo.
- El reintento después de un fallo temporal.
- La finalización correcta en el segundo intento.
- El procesamiento de mensajes duplicados.
- La conservación de un solo pago y un único descuento de inventario.
- La respuesta HTTP 404 para trabajos inexistentes.

El estado se consulta mediante polling con un tiempo máximo controlado. La prueba no depende de una espera fija para asumir que el procesamiento terminó.

## Correspondencia del flujo web

La prueba web utiliza Playwright y Page Object Model para automatizar un recorrido en SauceDemo.

El flujo representa de forma simplificada el escenario de Onboarding:

- El inicio de sesión representa el ingreso del comercio al portal.
- La selección de productos representa la selección del equipo POS.
- El carrito representa la revisión de los productos seleccionados.
- Los datos del checkout representan el registro de información de entrega.
- La confirmación de la compra representa el resultado exitoso del pago.

La prueba utiliza únicamente datos sintéticos y las credenciales públicas proporcionadas por SauceDemo.

La captura generada se guarda en:

```text
evidencias/compra_saucedemo.png
```

## Aislamiento y limpieza de datos

Las pruebas de API, pagos y asincronía crean una nueva instancia de la aplicación en memoria para cada caso.

Esto permite que:

- Cada prueba sea independiente.
- Los casos puedan ejecutarse en cualquier orden.
- No se compartan datos entre ejecuciones.
- Los datos desaparezcan al finalizar cada prueba.
- No sea necesario realizar una limpieza manual.

La prueba web utiliza información sintética y no contiene datos personales reales.

Los archivos temporales, cachés, entornos virtuales y reportes locales están excluidos mediante `.gitignore`.

## Integración continua

El archivo `.github/workflows/qa.yml` configura un pipeline de GitHub Actions.

El pipeline se ejecuta automáticamente en:

- Cada `push`.
- Cada `pull_request`.
- Ejecuciones manuales mediante `workflow_dispatch`.

El proceso realiza:

1. Descarga del repositorio.
2. Preparación de Python 3.13.
3. Instalación de dependencias.
4. Instalación de Chromium.
5. Ejecución de las pruebas automatizadas.

Si alguna prueba falla, el comando de Pytest devuelve un resultado de error y el pipeline queda bloqueado.

La prueba de JMeter se ejecuta localmente y no forma parte del pipeline actual.

## Evidencias

Las evidencias disponibles se encuentran en la carpeta `evidencias/`:

- `evidencias/compra_saucedemo.png`: captura del flujo web completado.
- `evidencias/carga_resultados.jtl`: resultados de la ejecución de JMeter.

Los resultados del pipeline pueden consultarse en la sección **Actions** del repositorio de GitHub.

## Decisiones de diseño

- Se implementó una API local con FastAPI para evitar dependencias de sistemas corporativos, credenciales y servicios AWS reales.
- Cada prueba crea una instancia independiente de la aplicación para mantener los datos aislados.
- La idempotencia se valida mediante una clave única y métricas internas verificables.
- Se comprueba que exista un solo pago lógico y un único descuento de inventario.
- Los procesos asíncronos se verifican consultando el estado del trabajo, sin depender únicamente de esperas fijas.
- La prueba web utiliza Playwright y Page Object Model para separar las acciones de la página de las validaciones.
- JMeter se ejecuta exclusivamente contra el simulador local.
- GitHub Actions ejecuta automáticamente las pruebas y bloquea el pipeline cuando alguna falla.
- Se priorizaron pocos escenarios representativos en lugar de buscar una cobertura exhaustiva.

## Limitaciones y mejoras futuras

Por el tiempo disponible se priorizaron los riesgos de mayor impacto: creación y consulta del tracking, pagos duplicados, descuento de inventario, reintentos asíncronos y el recorrido principal de compra.

Como mejoras futuras se implementarían:

- Umbrales automáticos de rendimiento para tiempo de respuesta, percentil 95, tasa de errores y transacciones por segundo.
- Parametrización completa de las URLs, usuarios, concurrencia y rampa de carga por ambiente.
- Separación del pipeline en etapas para pruebas API, transaccionales, asíncronas y web.
- Publicación automática de reportes y evidencias como artefactos del pipeline.
- Análisis estático del código.
- Escaneo automático de dependencias y vulnerabilidades.
- Pruebas de contrato para integraciones externas.
- Mayor cobertura de errores, estados intermedios y recuperación ante fallos.
- Sustitución o aislamiento de la aplicación web pública para evitar que su disponibilidad vuelva inestable el pipeline.

Estas mejoras se incorporarían progresivamente, manteniendo pruebas independientes, repetibles y sin información sensible.

## Estructura del proyecto

```text
qa-onboarding/
├── .github/
│   └── workflows/
│       └── qa.yml
├── app/
│   ├── __init__.py
│   └── main.py
├── evidencias/
│   ├── carga_resultados.jtl
│   └── compra_saucedemo.png
├── pages/
│   └── saucedemo_page.py
├── tests/
│   ├── api/
│   │   └── test_trackings.py
│   ├── async_tests/
│   │   └── test_payment_jobs.py
│   ├── load/
│   │   └── tracking_load.jmx
│   ├── transactional/
│   │   └── test_duplicate_payment.py
│   └── web/
│       └── test_checkout.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```