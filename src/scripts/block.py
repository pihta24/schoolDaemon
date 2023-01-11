from os import remove, popen, system
from re import search


try:
    out = popen("DISPLAY=:0 XAUTHORITY=/home/student/.Xauthority xinput --list")
    for i in out.readlines():
        if "mouse" in i.lower() or "keyboard" in i.lower():
            system('DISPLAY=:0 XAUTHORITY=/home/student/.Xauthority xinput --disable ' + search(r"id=(\d+)", i).group(1) + ' >/dev/null 2>&1')
except Exception as e:
    print(str(e))
