from datetime import datetime

import bs4 as bs4

from mysql import ara_cursor, newara_cursor, newara_db
from query import read_queries, write_queries


def _match_board(ara_id):
    return {
        1: 1,
        2: 7,
        3: 3,
        5: 7,
        8: 5,
        10: 7,
        17: 7,
        29: 7,
        30: 7,
        42: 6,
        43: 4,
        48: 7,
        49: 5,
        51: 6,
    }.get(ara_id, None)

def _sync_attachments():
    newara_files = []

    ara_cursor.execute(query=read_queries['files'] .format(500))
    files = ara_cursor.fetchall()
    ara_cursor.execute(query=read_queries['articles'] .format(500))
    articles = ara_cursor.fetchall()

    for f in files:
        article = get_article(articles, f['article_id'])
        if article:
            parsed = {
                'id': f['id'],
                'created_at': article['date'].isoformat(),
                'updated_at': article['date'].isoformat(),
                'deleted_at': (article['date'] if article['deleted'] else datetime.min).isoformat(),
                'file': 'files/{}/{}'.format(f['filepath'], f['saved_filename']),
                'mimetype': None,
                'size': None,
            }
            newara_files.append(tuple(parsed.values()))
    
    print(datetime.now(), 'sync attachment')
    newara_cursor.executemany(write_queries['core_attachment'], newara_files)
    newara_db.commit()


def _sync_articles():
    newara_articles = []

    ara_cursor.execute(query=read_queries['articles'] .format(500))
    articles = ara_cursor.fetchall()

    garbage_num = 0

    for article in articles:
        if article['parent_id'] is None:
            parsed = {
                'id': article['id'],
                'created_at': article['date'].isoformat(),
                'updated_at': article['date'].isoformat(),
                'deleted_at': (article['date'] if article['deleted'] else datetime.min).isoformat(),
                'title': article['title'],
                'content': article['content'],
                'content_text': ' '.join(bs4.BeautifulSoup(article['content'], features='html5lib').find_all(text=True)),
                'is_anonymous': False,
                'is_content_sexual': False,
                'is_content_social': False,
                'hit_count': article['hit'],
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'commented_at': article['last_reply_date'].isoformat(),
                'created_by_id': None,
                # 'created_by_id': article['author_id'],
                # 'created_by_nickname': article['nickname'],
                'parent_board_id': _match_board(article['board_id']),
            }

            if parsed['parent_board_id'] is not None:
                # print(article['id'])
                newara_articles.append(tuple(parsed.values()))
            else:
                garbage_num+=1

    print("garbage num {}" .format(garbage_num))
    print(datetime.now(), 'sync articles')

    newara_cursor.executemany(write_queries['core_article'], newara_articles)
    newara_db.commit()


def _sync_article_attachments():
    newara_article_attachments = []
    
    ara_cursor.execute(query=read_queries['files'] .format(500))
    files = ara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_article'].format(500))
    new_articles = newara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_attachment'].format(500))
    new_attachments = newara_cursor.fetchall()
    fid = 1
    
    for f in files:
        article = get_article(new_articles, f['article_id'])
        if article:
            parsed = {
                'id': fid,
                'article_id': article['id'],
                'attachment_id': f['id'],
            }
            newara_article_attachments.append(tuple(parsed.values()))
            fid += 1
    
    print(datetime.now(), 'sync article attachments')
    newara_cursor.executemany(write_queries['core_article_attachments'], newara_article_attachments)
    newara_db.commit()


def _sync_comments():
    newara_comments = []

    ara_cursor.execute(query=read_queries['articles'].format(500))
    articles = ara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_article'].format(500))
    new_articles = newara_cursor.fetchall()
    ara_cursor.execute(query=read_queries['files'].format(500))
    files = ara_cursor.fetchall()

    for article in articles:
        if article['parent_id'] is not None and article['root_id'] == article['parent_id']:
            parsed = {
                'id': article['id'],
                'created_at': article['date'].isoformat(),
                'updated_at': article['date'].isoformat(),
                'deleted_at': (article['date'] if article['deleted'] else datetime.min).isoformat(),
                'content': article['content'],
                'is_anonymous': False,
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'attachment_id': get_attachment_id(files, article['id']),
                'created_by_id': None,
                'parent_article_id': get_parent_article_id(new_articles, article['root_id']),
                'parent_comment_id': None,
            }

            newara_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'sync comments')
    newara_cursor.executemany(write_queries['core_comment'], newara_comments)
    newara_db.commit()


def _sync_co_comments():
    newara_co_comments = []

    ara_cursor.execute(query=read_queries['articles'].format(500))
    articles = ara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_article'].format(500))
    new_articles = newara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_comment'].format(500))
    new_comments = newara_cursor.fetchall()
    ara_cursor.execute(query=read_queries['files'].format(500))
    files = ara_cursor.fetchall()

    for article in articles:
        if article['parent_id'] is not None and article['root_id'] != article['parent_id']:
            parsed = {
                'id': article['id'],
                'created_at': article['date'].isoformat(),
                'updated_at': article['date'].isoformat(),
                'deleted_at': (article['date'] if article['deleted'] else datetime.min).isoformat(),
                'content': article['content'],
                'is_anonymous': False,
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'attachment_id': get_attachment_id(files, article['id']),
                'created_by_id': None,
                'parent_article_id': get_parent_article_id(new_articles, article['root_id']),
                'parent_comment_id': get_parent_comment_id(new_comments, newara_co_comments, article['root_id'], article['parent_id']),
            }

            newara_co_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'sync cocomments')
    newara_cursor.executemany(write_queries['core_comment'], newara_co_comments)
    newara_db.commit()

def get_article(articles, article_id):
    for article in articles:
        if article['id'] == article_id:
            return article
    return None


def get_attachment_id(files, article_id):
    for f in files:
        if f['article_id'] == article_id:
            return f['id']
    return None

def get_parent_article_id(new_articles, root_id):
    for new_article in new_articles:
        if new_article['id'] == root_id:
            return new_article['id']
    return None

def get_parent_comment_id(new_comments, newara_co_comments, root_id, parent_id):
    for new_comment in new_comments:
        if new_comment['parent_article_id'] == root_id and new_comment['id'] == parent_id:
            return new_comment['id']
    for newara_co_comment in newara_co_comments:
        if newara_co_comment[0] == parent_id:
            return newara_co_comment[11]
    return None

def sync():
    _sync_attachments()
    _sync_articles()
    _sync_article_attachments()
    _sync_comments()
    _sync_co_comments()
    print(datetime.now(), 'insertion finished')
