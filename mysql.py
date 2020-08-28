import pymysql

ara_db = pymysql.connect(
        user='root',
        passwd='',
        host='127.0.0.1',
        db='ara',
        charset='utf8'
    )

ara_cursor = ara_db.cursor(pymysql.cursors.DictCursor)

newara_middle_db = pymysql.connect(
        user='root',
        passwd='',
        host='127.0.0.1',
        db='new_ara_migration',
        charset='utf8'
    )

newara_middle_cursor = newara_middle_db.cursor(pymysql.cursors.DictCursor)

newara_consecutive_db = pymysql.connect(
        user='root',
        passwd='',
        host='127.0.0.1',
        db='new_ara_consecutive',
        charset='utf8'
    )

newara_consecutive_cursor = newara_consecutive_db.cursor(pymysql.cursors.DictCursor)
