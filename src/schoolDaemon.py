import daemon
from main import main


def daemonize():
    with daemon.DaemonContext():
        main()


if __name__ == "__main__":
    daemonize()
