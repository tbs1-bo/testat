#!/bin/bash

. .env

echo "update repo at server $DEPLOY_SERVER"
ssh $DEPLOY_SERVER "git -C $DEPLOY_DIR pull"

echo "outdated deps:"
ssh $DEPLOY_SERVER "cd $DEPLOY_DIR && ~/.local/bin/poetry show --no-dev --outdated"

echo "update deps:"
ssh $DEPLOY_SERVER "cd $DEPLOY_DIR && ~/.local/bin/poetry update --no-dev"

echo "restart service"
ssh -t $DEPLOY_SERVER 'sudo supervisorctl restart testat'
