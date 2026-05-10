# source scripts/auto_venv_cd.sh
_auto_venv_cd() {
  cd "$@" || return
  if [ -f "./venv/bin/activate" ]; then
    . ./venv/bin/activate
    echo "[auto-venv] activated: $(pwd)/venv"
  fi
}
alias cdp='_auto_venv_cd'
