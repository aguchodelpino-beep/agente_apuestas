#!/usr/bin/env bash
set -euo pipefail

cd /home/aguchodelpino/agente_apuestas || exit 1

if ! command -v node >/dev/null 2>&1; then
  echo "❌ Node.js no está instalado"
  echo "Instala Node 20+ y vuelve a correr este script"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "❌ npm no está instalado"
  exit 1
fi

cp .env ".env.bak_balldontlie_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
touch .env

python3 - <<'PY'
from pathlib import Path
import re

KEY_NAME = "BALLDONTLIE_API_KEY"
KEY_VALUE = "PON_AQUI_TU_KEY_REAL"

p = Path(".env")
txt = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""
line = f"{KEY_NAME}={KEY_VALUE}"
pat = re.compile(rf"^\s*{re.escape(KEY_NAME)}\s*=.*$", re.M)

if pat.search(txt):
    txt = pat.sub(line, txt)
else:
    if txt and not txt.endswith("\n"):
        txt += "\n"
    txt += line + "\n"

p.write_text(txt, encoding="utf-8")
print("OK .env actualizado con BALLDONTLIE_API_KEY")
PY

npm view balldontlie-mcp version >/dev/null 2>&1 && echo "OK paquete balldontlie-mcp visible en npm" || echo "WARN no se pudo verificar balldontlie-mcp"
npm view @balldontlie/mcp-server version >/dev/null 2>&1 && echo "OK paquete @balldontlie/mcp-server visible en npm" || echo "WARN no se pudo verificar @balldontlie/mcp-server"

cat > mcp/balldontlie_mcp_client.json <<'JSON'
{
  "mcpServers": {
    "balldontlie": {
      "command": "npx",
      "args": ["-y", "balldontlie-mcp"],
      "env": {
        "BALLDONTLIE_API_KEY": "PON_AQUI_TU_KEY_REAL"
      }
    }
  }
}
JSON

echo "✅ Instalación base lista"
echo "1) Reemplaza PON_AQUI_TU_KEY_REAL en .env y mcp/balldontlie_mcp_client.json"
echo "2) Prueba manual:"
echo '   BALLDONTLIE_API_KEY=tu_key npx -y balldontlie-mcp'
