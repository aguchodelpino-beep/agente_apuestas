# AGENTE_APUESTAS 2.0

## Regla de trabajo obligatoria

Antes de tocar cualquier archivo o proponer cualquier cambio, el orden obligatorio es:

1. `bash scripts/agent_status.sh`
2. `bash scripts/run_audit.sh`
3. Recién después, cualquier parche, script o desarrollo nuevo.

Objetivo:
- empezar siempre con contexto actualizado;
- no asumir estado del proyecto;
- evitar reanálisis largos e innecesarios;
- detectar primero qué ya está hecho y qué falta.
