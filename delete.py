from datetime import datetime

from sync import sync
from mysql import newara_cursor, newara_db
from query import read_queries, delete_queries


def main():
    print(datetime.now(), 'delete start')

    ### Delete articles ###
    # newara_cursor.execute(query=read_queries['core_comment'].format(500))
    # new_comments = newara_cursor.fetchall()
    # newara_cursor.execute(query=read_queries['core_article_attachments'].format(500))
    # new_article_attachments = newara_cursor.fetchall()

    # for i in range(len(new_comments)):
    #     newara_cursor.execute(query=delete_queries['core_comment'])
    
    # newara_cursor.execute(query=delete_queries['core_article_attachments'].format(len(new_article_attachments)))
    # newara_db.commit()

    # newara_cursor.execute(query=read_queries['core_article'].format(500))
    # new_articles = newara_cursor.fetchall()
    # newara_cursor.execute(query=read_queries['core_attachment'].format(500))
    # new_attachments = newara_cursor.fetchall()

    # newara_cursor.execute(query=delete_queries['core_article'].format(len(new_articles)))
    # newara_cursor.execute(query=delete_queries['core_attachment'].format(len(new_attachments)))
    # newara_db.commit()

    ########################
    
    newara_cursor.execute(query=read_queries['user_userprofile'].format(100))
    user_profile = newara_cursor.fetchall()
    newara_cursor.execute(query=delete_queries['user_userprofile'].format(len(user_profile)))
    newara_db.commit()

    newara_cursor.execute(query=read_queries['auth_user'].format(100))
    auth_user = newara_cursor.fetchall()
    newara_cursor.execute(query=delete_queries['auth_user'].format(len(auth_user)))
    newara_db.commit()

    print(datetime.now(), 'delete users finished')


if __name__ == '__main__':
    main()
