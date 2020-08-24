from datetime import datetime

from sync import sync
from sync_users import sync_users
from consecutive import make_consecutive_id

import time



def main():
    print(datetime.now(), 'main start')
    start = time.time()
    sync_users()
    sync()
    make_consecutive_id()
    end = time.time()
    print("Migration took {} seconds".format(end-start))


if __name__ == '__main__':
    main()
