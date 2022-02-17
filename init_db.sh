#!/bin/bash

. .env

echo "Create tables"
python3 -c 'import testate;testate.db.create_all()'
echo "Add first user $FIRST_USERNAME"
python3 -c "import testate as t;t.db.session.add(t.DBUser(uid=\"$FIRST_USERNAME\"));t.db.session.commit()"
