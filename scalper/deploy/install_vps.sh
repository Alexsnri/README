#!/usr/bin/env bash
# Instala el bot en un servidor Linux (Ubuntu/Debian; por ejemplo Oracle Cloud "Always Free").
# Desde el celular: abre la consola del proveedor (Cloud Shell / consola SSH del navegador) y pega:
#   curl -fsSL https://raw.githubusercontent.com/Alexsnri/README/main/scalper/deploy/install_vps.sh -o install.sh
#   less install.sh        # revísalo antes de correrlo
#   bash install.sh
# Arranca solo al prender el servidor (docker --restart=always) y guarda el estado en el volumen "scalper-data".
set -euo pipefail
REPO="${REPO:-https://github.com/Alexsnri/README.git}"
BRANCH="${BRANCH:-main}"
DIR="$HOME/scalper-bot"

if ! command -v docker >/dev/null; then
  echo "Instalando Docker…"; sudo apt-get update -y && sudo apt-get install -y docker.io git
  sudo systemctl enable --now docker
fi
if [ ! -d "$DIR" ]; then git clone --depth 1 -b "$BRANCH" "$REPO" "$DIR"; else git -C "$DIR" pull --ff-only; fi
cd "$DIR/scalper"

if [ ! -f .env ]; then
  echo "Primera vez: pega tus credenciales (no se muestran ni se suben a ningún lado)."
  read -rp  "API key de Capital.com: " K; read -rp "Correo de Capital.com: " I
  read -rsp "Contraseña personalizada de la API: " P; echo
  read -rp  "Token de Telegram (Enter para omitir): " T
  read -rsp "Contraseña para el dashboard: " D; echo
  umask 077
  printf 'CAPITAL_API_KEY=%s\nCAPITAL_IDENTIFIER=%s\nCAPITAL_API_PASSWORD=%s\nTELEGRAM_TOKEN=%s\nDASHBOARD_PASSWORD=%s\n' "$K" "$I" "$P" "$T" "$D" > .env
fi

sudo docker build -t scalper .
sudo docker rm -f scalper 2>/dev/null || true
sudo docker run -d --name scalper --restart=always -p 80:8080 --env-file .env -v scalper-data:/data scalper
echo "Listo. Abre http://IP-DE-TU-SERVIDOR/ en el celular (abre el puerto 80 en el firewall del proveedor)."
echo "Reporte: sudo docker exec scalper python -m bot.reporte   ·   Logs: sudo docker logs -f scalper"
