import pymysql

ara_db = pymysql.connect(
        user='root',
        passwd='',
        host='127.0.0.1',
        db='ara',
        charset='utf8'
    )

ara_cursor = ara_db.cursor(pymysql.cursors.DictCursor)

newara_db = pymysql.connect(
        user='root',
        passwd='',
        host='127.0.0.1',
        db='new_ara',
        charset='utf8'
    )

newara_cursor = newara_db.cursor(pymysql.cursors.DictCursor)
