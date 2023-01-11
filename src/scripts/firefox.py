from os import system
from sys import argv


system(f'DISPLAY=:0 HOME=/home/student/ su - student -c "firefox --new-window {argv[1]} --kiosk" > /dev/null 2>&1 &')
