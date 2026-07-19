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
