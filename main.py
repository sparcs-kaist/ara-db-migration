from datetime import datetime

from sync import sync
from sync_users import sync_users


def main():
    print(datetime.now(), 'main start')
    # sync()
    sync_users()


if __name__ == '__main__':
    main()
