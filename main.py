from datetime import datetime

from sync import sync


def main():
    print(datetime.now(), 'main start')
    sync()


if __name__ == '__main__':
    main()
