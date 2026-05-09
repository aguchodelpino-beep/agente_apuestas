# agente_apuestas 2.0 — reglas obligatorias

## Estructura oficial
- core/: config, logging, auth, health
- departments/deportes/futbol/: handlers, service, repo, models
- departments/deportes/tenis/: handlers, service, repo, models
- departments/deportes/basket/: handlers, service, repo, models
- departments/visuales/: formatter, markdown, cards, telegram_ui
- departments/analitica/: métricas y scoring
- departments/bankroll/: stake, Kelly, límites
- departments/ml/: inferencia y modelos
- departments/sistema/: wiring, bootstrap, jobs internos
- shared/: utilidades puras reutilizables
- telegram_bot.py: integración Telegram
- main.py: arranque

## Flujo obligatorio
telegram_bot -> handlers -> service -> repo/models/shared -> visuales -> telegram_bot

## Prohibido
- lógica pesada en handlers
- formateo en repo
- acceso a Telegram desde service
- imports cruzados entre deportes
- crear archivos Python sueltos en raíz fuera de main.py y telegram_bot.py
