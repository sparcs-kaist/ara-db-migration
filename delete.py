from datetime import datetime

from sync import sync
from mysql import newara_cursor, newara_db
from query import read_queries, delete_queries


def main():
    FETCH_NUM = 80000

    print(datetime.now(), 'delete start')

    ### Delete articles ###
    newara_cursor.execute(query=read_queries['core_comment'].format(FETCH_NUM))
    new_comments = newara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_article_attachments'].format(FETCH_NUM))
    new_article_attachments = newara_cursor.fetchall()

    for i in range(len(new_comments)):
        newara_cursor.execute(query=delete_queries['core_comment'])
    
    newara_cursor.execute(query=delete_queries['core_article_attachments'].format(len(new_article_attachments)))
    newara_db.commit()

    newara_cursor.execute(query=read_queries['core_article'].format(FETCH_NUM))
    new_articles = newara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    new_attachments = newara_cursor.fetchall()

    newara_cursor.execute(query=delete_queries['core_article'].format(len(new_articles)))
    newara_cursor.execute(query=delete_queries['core_attachment'].format(len(new_attachments)))
    newara_db.commit()

    print(datetime.now(), 'delete articles finished')

    ########################
    
    newara_cursor.execute(query=read_queries['user_userprofile'].format(FETCH_NUM))
    user_profile = newara_cursor.fetchall()
    newara_cursor.execute(query=delete_queries['user_userprofile'].format(len(user_profile)))
    newara_db.commit()

    newara_cursor.execute(query=read_queries['auth_user'].format(FETCH_NUM))
    auth_user = newara_cursor.fetchall()
    newara_cursor.execute(query=delete_queries['auth_user'].format(len(auth_user)))
    newara_db.commit()

    print(datetime.now(), 'delete users finished')


if __name__ == '__main__':
    main()
