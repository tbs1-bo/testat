from cgi import test
from testate import Card
import sys

def main():
    if len(sys.argv) != 2:
        print("ls, rm, hide or show?")
        return

    if sys.argv[1] == 'ls':
        for card in Card.query.group_by(Card.project_name):
            print(f'{card.project_name} ({len(card.milestones)}) visible={card.is_visible}')
        
    elif sys.argv[1] == 'rm':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'delete card {card.id} of {card.student_name}')
            card.delete()

    elif sys.argv[1] == 'hide':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'hiding card of {card.student_name}')
            card.visibility(False)

    elif sys.argv[1] == 'show':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'unhiding card of {card.student_name}')
            card.visibility(True)

    else:
        print(f'unsupported command')

if __name__ == '__main__':
    main()
