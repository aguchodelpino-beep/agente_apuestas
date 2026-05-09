# Agente Apuestas

Proyecto modular para agregación de fixtures deportivos, cache local JSON y scheduler persistente.

## Estructura

- `core/`: configuración, logging, health.
- `shared/`: utilidades comunes, cache, odds, providers.
- `departments/deportes/`: módulos por deporte.
- `scheduler.py`: jobs programados con APScheduler.
- `main.py`: punto de entrada principal.

## Entorno

1. Crear entorno virtual:
   `python3 -m venv venv`
2. Activar entorno:
   `source venv/bin/activate`
3. Instalar dependencias:
   `pip install -r requirements.txt`

## Buenas prácticas

- Usar entorno virtual aislado. 
- Fijar versiones de dependencias para instalaciones reproducibles.
- Mantener dependencias mínimas y revisar las no usadas.
- Centralizar configuración en `core/config.py`.
- No usar `os.getenv()` fuera de `core/config.py`.
- No llamar APIs desde `repo.py`; solo desde providers.
- Leer datos diarios desde JSON local en repos.
- Usar scheduler para refrescos controlados.

## Dependencias mínimas sugeridas

- `requests`
- `apscheduler`
- `sqlalchemy`

## Flujo recomendado

1. Scheduler descarga fixtures por deporte.
2. Providers normalizan datos.
3. Cache guarda JSON por día.
4. Repo lee JSON local.
5. Service consume repo.
6. Bot/UI consume services.
