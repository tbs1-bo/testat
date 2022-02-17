import testate
import os

print("Create tables")
testate.db.create_all()

if "FIRST_USERNAME" in os.environ:
    uid = os.environ["FIRST_USERNAME"]
else:
    print('env var FIRST_USERNAME not found. Fallback: ask user')
    uid = input('First userid? ')

testate.db.session.add(testate.DBUser(uid=uid))
testate.db.session.commit()
