# Evaluación QA: Onboarding Digital

Repositorio semilla. Primera etapa: servicio simulado y pruebas de API locales.
Las pruebas transaccionales, asíncronas, web, de carga y el pipeline se incorporarán en commits posteriores.

## Requisitos

- Python 3.13 o 3.14 y Git
- No requiere credenciales ni servicios externos para la primera etapa.

## Instalación (PowerShell en VS Code)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecutar esta etapa

```powershell
.\.venv\Scripts\python.exe -m pytest tests/api -v
```

Para ver el servicio de forma interactiva:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abrir http://127.0.0.1:8000/docs y detener con Ctrl+C.

## Estructura prevista

- `app/`: servicio local con datos sintéticos.
- `tests/api/`: API positiva y negativa.
- `tests/transactional/`: pagos duplicados (siguiente etapa).
- `tests/async_tests/`: colas y reintentos (siguiente etapa).
- `pages/` y `tests/web/`: flujo web con POM (etapa posterior).
- `load/`: carga local con umbrales (etapa posterior).
- `.github/workflows/`: CI (etapa posterior).

Cada prueba utiliza su propia aplicación en memoria para no depender del orden ni compartir datos.
