from os.path import abspath


commands = {
    b"ffx": f"python3 {abspath('scripts/firefox.py')} ",
    b"blc": f"python3 {abspath('scripts/block.py')}",
    b"ubl": f"python3 {abspath('scripts/unblock.py')}",
    b"ntf": f"python3 {abspath('scripts/notify.py')} ",
    b"pau": f"python3 {abspath('scripts/policy_auth.py')}",
    b"pno": f"python3 {abspath('scripts/policy_no.py')}",
    b"shd": "shutdown -h now",
    b"rbt": "reboot",
    b"los": "loginctl terminate-user student",
    b"pip": "python3 -m ensurepip",
    b"est": "chmod o+x /usr/lib/kf5/bin/systemsettings",
    b"dst": "chown :wheel /usr/lib/kf5/bin/systemsettings && chmod o-x /usr/lib/kf5/bin/systemsettings"
}
