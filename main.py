from datetime import datetime

from sync import sync
from sync_users import sync_users
from consecutive import make_consecutive_id
from relink import update_ara_links
from change_attachment_name import change_attachment_name_in_s3

import time


def main():
    print(datetime.now(), 'main start')
    start = time.time()
    sync_users()
    sync()
    make_consecutive_id()
    update_ara_links()
    end = time.time()
    print("Migration took {} seconds".format(end-start))


if __name__ == '__main__':
    main()
