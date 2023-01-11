from os import system
from sys import argv

system(f'DISPLAY=:0 XAUTHORITY=/home/student/.Xauthority kdialog --msgbox "{argv[1]}" > /dev/null 2>&1 &')
