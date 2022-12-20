from cgi import test
import testate
import sys

def run(cmd):
    if cmd == 'add':
        uid = input('Username? ')
        dbu = testate.DBUser(uid=uid)
        testate.db.session.add(dbu)
        testate.db.session.commit()

    elif cmd == 'ls':
        for user in testate.User.all():
            print(user)
        
    elif cmd == 'rm':
        uid = input('Username? ')
        u = testate.User(uid)
        u.delete()

    else:
        print(f'unsupported command')

def main():
    if len(sys.argv) != 2:
        print("add, ls or rm?")
        return

    with testate.app.app_context():
        run(sys.argv[1])

if __name__ == '__main__':
    main()
