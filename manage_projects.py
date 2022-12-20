from testate import Card, app
import sys

def run(cmd):
    if cmd == 'ls':
        print('project name \t| #milestones \t| visible')
        for card in Card.query.group_by(Card.project_name):
            print(f'{card.project_name} \t| {len(card.milestones)} \t| {card.is_visible}')
        
    elif cmd == 'rm':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'delete card {card.id} of {card.student_name}')
            card.delete()

    elif cmd == 'hide':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'hiding card of {card.student_name}')
            card.visibility(False)

    elif cmd == 'show':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'unhiding card of {card.student_name}')
            card.visibility(True)

    else:
        print(f'unsupported command')

def main():
    if len(sys.argv) != 2:
        print("ls, rm, hide or show?")
        return

    with app.app_context():
        run(sys.argv[1])


if __name__ == '__main__':
    main()
