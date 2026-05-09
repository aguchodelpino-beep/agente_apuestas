# ARCHITECTURE

## Propósito

Este proyecto es un motor modular de agregación de apuestas deportivas que vive sobre cache local, no sobre consultas constantes a APIs en tiempo real.

El objetivo del sistema es:

- ingerir datos de varias fuentes de forma programada,
- normalizar y deduplicar fixtures,
- guardar snapshots locales por día,
- exponer acceso simple por deporte,
- generar picks y alertas sin depender de la API en cada consulta,
- dejar lista la base para analítica, ML y bankroll más adelante.

---

## Regla principal

La dependencia debe fluir hacia adentro.

- `providers` hablan con APIs externas.
- `scheduler` coordina refresh y cache.
- `repo.py` solo lee datos locales.
- `service.py` aplica reglas de negocio por deporte.
- `handlers.py` conecta servicios con Telegram o el orquestador.
- `telegram_bot.py` presenta resultados y comandos.
- `departments/analitica`, `departments/ml` y `departments/bankroll` se apoyan en datos ya normalizados.

Si una capa necesita otra, la inferior no debe depender de la superior.

---

## Flujo de datos

```text
APIs externas
    ↓
shared/providers/*
    ↓
scheduler.py
    ↓
cache JSON local por deporte/día
    ↓
departments/*/repo.py
    ↓
departments/*/service.py
    ↓
handlers.py / telegram_bot.py
    ↓
usuario final
```

---

## Capas del sistema

### 1) Providers

Responsabilidad:
- llamar APIs externas,
- manejar errores, 429 y timeouts,
- normalizar el shape inicial del dato,
- devolver listas de diccionarios listas para cache.

Reglas:
- Nunca guardar archivos.
- Nunca tomar decisiones de negocio.
- Nunca generar picks.
- Nunca llamar a Telegram.

Archivos:
- `shared/providers/futbol_provider.py`
- `shared/providers/tenis_provider.py`
- `shared/providers/basket_provider.py`
- `shared/providers/provider_utils.py`

---

### 2) Scheduler

Responsabilidad:
- ejecutar refresh programados,
- llamar providers,
- fusionar datos nuevos con datos existentes,
- guardar el resultado en cache local,
- mantener historial de ejecuciones,
- registrar jobs persistentes en SQLite.

Reglas:
- No debe contener lógica de picks.
- No debe conocer Telegram.
- No debe calcular edge ni confianza.
- Solo orquesta la ingesta.

Archivos:
- `scheduler.py`
- `main.py`

---

### 3) Cache local

Responsabilidad:
- conservar datos por deporte y por día,
- servir como fuente principal del sistema durante el día,
- permitir lecturas rápidas y predecibles.

Reglas:
- Es la fuente de verdad operativa diaria.
- Si la API falla, la cache sigue alimentando el sistema.
- Los repos nunca deben saltarse esta capa para ir a la API.

Ubicación:
- `data/raw/<deporte>/<YYYY-MM-DD>.json`
- `data/cache/scheduler/*.json`

---

### 4) Repositorios

Responsabilidad:
- leer JSON local,
- devolver fixtures, odds, resultados y snapshots,
- ofrecer méconjunto completos simples de consulta por deporte.

Reglas:
- Nunca llamar APIs.
- Nunca refrescar cache.
- Nunca mezclar lógica de negocio.
- Solo lectura local.

Archivos:
- `departments/deportes/futbol/repo.py`
- `departments/deportes/tenis/repo.py`
- `departments/deportes/basket/repo.py`

---

### 5) Servicios

Responsabilidad:
- aplicar reglas por deporte,
- filtrar fixtures relevantes,
- construir candidatos a pick,
- priorizar el día,
- preparar datos para analítica y Telegram.

Reglas:
- Usan solo repos.
- No llaman APIs.
- No escriben cache.
- No contienen lógica de transporte.

Archivos:
- `departments/deportes/futbol/service.py`
- `departments/deportes/tenis/service.py`
- `departments/deportes/basket/service.py`

---

### 6) Handlers

Responsabilidad:
- recibir comandos del bot o del orquestador,
- elegir el deporte o flujo correcto,
- devolver respuestas listas para UI.

Reglas:
- No hacen cómputo pesado.
- No acceden directamente a APIs.
- No contienen lógica de datos crudos.

Archivo esperado:
- `handlers.py`

---

### 7) Telegram UI

Responsabilidad:
- convertir datos en mensajes claros,
- renderizar Markdown limpio,
- crear botones y formato reutilizable,
- mantener una experiencia consistente.

Reglas:
- No decide qué pick existe.
- No calcula probabilidades.
- Solo presenta resultados.

Archivos:
- `visuales/markdown.py`
- `visuales/telegram_ui.py`
- `telegram_bot.py`

---

### 8) Analítica

Responsabilidad:
- calcular edge,
- estimar fair odds,
- medir valor esperado,
- derivar confianza y CLV esperado.

Reglas:
- Consume servicios o datos ya normalizados.
- No toca providers.
- No toca Telegram.
- No refresca cache.

Archivo esperado:
- `departments/analitica/*`

---

### 9) ML

Responsabilidad:
- features,
- entrenamiento,
- scoring,
- ensemble por deporte y mercado.

Reglas:
- Se apoya en datos estables.
- No debe ser la primera capa del sistema.
- No debe resolver problemas de ingesta.

Archivo esperado:
- `departments/ml/*`

---

### 10) Bankroll

Responsabilidad:
- stake sizing,
- Kelly fraccional,
- límites por liga,
- exposición y riesgo.

Reglas:
- Usa inputs limpios desde analítica o service.
- No corrige problemas de datos.
- No decide el shape de la cache.

Archivo esperado:
- `departments/bankroll/*`

---

## Estructura recomendada

```text
agente_apuestas/
├── core/
├── data/
├── departments/
│   ├── deportes/
│   │   ├── futbol/
│   │   ├── tenis/
│   │   └── basket/
│   ├── analitica/
│   ├── ml/
│   └── bankroll/
├── shared/
│   ├── cache.py
│   ├── datetime_utils.py
│   ├── odds.py
│   ├── validators.py
│   └── providers/
├── visuales/
├── tests/
├── scheduler.py
├── telegram_bot.py
├── handlers.py
├── main.py
└── ROADMAP.md
```

---

## Modelo de objetos base

Los modelos principales del sistema deben ser:

- `Fixture`: partido, jugador o evento base.
- `MarketOdds`: cuotas de un mercado concreto.
- `Pick`: candidato o selección recomendada.
- `Result`: resultado final del evento.
- `Snapshot`: estado del evento o mercado en un instante.

Regla:
- Los modelos viven en la capa de dominio o datos compartidos.
- No deben depender de Telegram ni de providers concretos.

---

## Estrategia de actualización

### Modo diario
Durante el día, el sistema debe operar leyendo cache local.

### Modo programado
El scheduler refresca en horario controlado:
- madrugada,
- mediodía,
- tarde.

### Modo degradado
Si una API falla o responde 429:
- no se rompe el flujo,
- se conserva la última cache válida,
- se registra el fallo,
- se sigue trabajando con lo ya disponible.

---

## Normalización

La normalización debe ocurrir antes de guardar y antes de comparar.

Debe unificar:
- nombres de ligas,
- nombres de equipos o jugadores,
- nombres de mercados,
- timestamps,
- IDs externos,
- formato de live/status.

La normalización evita que el mismo evento se vea como dos eventos distintos según el proveedor.

---

## Deduplicación

Antes de guardar nuevos datos:
- comparar por `fixture_id`,
- comparar por fecha y participantes cuando haga falta,
- actualizar solo si cambió estado, cuota o metadato importante.

Regla:
- No guardar duplicados.
- No sobrescribir información útil sin necesidad.
- No duplicar snapshots de la misma entidad.

---

## Resolución de identidad

Esta capa se deja para después porque es la más delicada.

Objetivo:
- detectar que `Barcelona vs Emelec` y `Barcelona SC vs Club Sport Emelec` son el mismo evento,
- empatar eventos entre proveedores distintos,
- mapear cambios de nombres o IDs.

Regla:
- Solo se activa cuando la normalización y la deduplicación ya funcionan bien.
- No debe bloquear la primera versión productiva.

---

## Orden de implementación

1. Congelar estructura objetivo.
2. Consolidar cache JSON local.
3. Mantener providers separados por deporte.
4. Repos locales.
5. Services por deporte.
6. Scheduler persistente con SQLite.
7. Telegram UI estable.
8. Analítica.
9. ML.
10. Bankroll.
11. Resolución de identidad avanzada.
12. Reintegración selectiva de agentes.

---

## Qué debe hacer cada archivo

### `shared/providers/*`
Traer datos externos.

### `scheduler.py`
Disparar y guardar refresh.

### `departments/*/repo.py`
Leer datos locales.

### `departments/*/service.py`
Aplicar reglas de negocio.

### `handlers.py`
Conectar servicios con el orquestador.

### `telegram_bot.py`
Exponer comandos y respuestas.

### `main.py`
Arrancar el sistema completo.

---

## Qué no debe pasar

- `repo.py` no debe llamar APIs.
- `service.py` no debe escribir JSON.
- `telegram_bot.py` no debe saber de RapidAPI.
- `providers` no deben generar picks.
- `ML` no debe compensar una ingesta rota.

---

## Regla final

Si una capa superior empieza a arreglar problemas de una capa inferior, la arquitectura está mal.

Primero datos.
Luego repos.
Luego servicios.
Luego producto.
Luego inteligencia.
