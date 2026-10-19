#!/bin/bash
set -euo pipefail

. .env

echo "update repo at server $DEPLOY_SERVER"
ssh "$DEPLOY_SERVER" "git -C \"$DEPLOY_DIR\" pull"

echo "outdated deps:"
ssh "$DEPLOY_SERVER" "cd \"$DEPLOY_DIR\" && ~/.local/bin/poetry show --without=dev --outdated"

echo "install deps (from poetry.lock):"
ssh "$DEPLOY_SERVER" "cd \"$DEPLOY_DIR\" && ~/.local/bin/poetry install --without=dev"

echo "restart service"
ssh -t "$DEPLOY_SERVER" 'sudo supervisorctl restart testat'

# App läuft hinter dem Reverse Proxy unter dem Pfad /testat (SCRIPT_NAME)
echo "smoke test"
ssh "$DEPLOY_SERVER" "cd \"$DEPLOY_DIR\" && . ./.env && base=http://\$TESTAT_IP:\$TESTAT_PORT/testat && \
  for i in \$(seq 10); do \
    [ \"\$(curl -s -o /dev/null -w '%{http_code}' \$base/login)\" = 200 ] && break; \
    sleep 1; \
  done && \
  login=\$(curl -s -o /dev/null -w '%{http_code}' \$base/login) && \
  azure=\$(curl -s -o /dev/null -w '%{http_code}' \$base/login_azure) && \
  echo \"/login: \$login, /login_azure: \$azure\" && \
  [ \"\$login\" = 200 ] && [ \"\$azure\" = 302 ]" \
  || { echo "smoke test fehlgeschlagen"; exit 1; }
