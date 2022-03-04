#!/bin/bash

. .env

echo "update repo at server $DEPLOY_SERVER"
ssh $DEPLOY_SERVER "git -C $DEPLOY_DIR pull"

echo "restart service"
ssh -t main.tbs1.de 'sudo supervisorctl restart testat'
