from cgi import test
import testate
import sys

def main():
    if len(sys.argv) != 2:
        print("add, ls or rm?")
        return

    if sys.argv[1] == 'add':
        # add
        uid = input('Username? ')
        dbu = testate.DBUser(uid=uid)
        testate.db.session.add(dbu)
        testate.db.session.commit()

    elif sys.argv[1] == 'ls':
        for user in testate.User.all():
            print(user)
        
    elif sys.argv[1] == 'rm':
        uid = input('Username? ')
        u = testate.User(uid)
        u.delete()

    else:
        print(f'unsupported command')

if __name__ == '__main__':
    main()
