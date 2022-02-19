from cgi import test
from testate import Card
import sys

def main():
    if len(sys.argv) != 2:
        print("ls or rm?")
        return

    if sys.argv[1] == 'ls':
        for card in Card.query.group_by(Card.project_name):
            print(f'{card.project_name} ({len(card.milestones)})')
        
    elif sys.argv[1] == 'rm':
        pname = input('Projekt? ')
        for card in Card.query.filter(Card.project_name == pname):
            print(f'delete of {card.student_name}')
            card.delete()

    else:
        print(f'unsupported command')

if __name__ == '__main__':
    main()
