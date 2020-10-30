from datetime import datetime

from sync import sync
from sync_users import sync_users
from sync_s3 import sync_s3
from consecutive import make_consecutive_id
from relink import update_ara_links

import time


def main():
    print(datetime.now(), 'main start')
    start = time.time()
    sync_users()
    sync()
    make_consecutive_id()
    update_ara_links()
    sync_s3()
    end = time.time()
    print("Migration took {} seconds".format(end-start))


if __name__ == '__main__':
    main()
