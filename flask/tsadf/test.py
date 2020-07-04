from time import sleep
import sys

for i in range(3):
    print('Yes or no?')
    sys.stdout.flush()
    choice = sys.stdin.readline().rstrip()
    if choice == 'y':
        print('Yes indeed!')
        sys.stdout.flush()
    else:
        print('Try again...')
        sys.stdout.flush()
    sleep(2)

for i in range(3):
    print('No or yes?')
    sys.stdout.flush()
    choice = sys.stdin.readline().rstrip()
    if choice == 'n':
        print('No indeed!')
        sys.stdout.flush()
        break
    else:
        print('Try again...')
        sys.stdout.flush()
    sleep(2)
