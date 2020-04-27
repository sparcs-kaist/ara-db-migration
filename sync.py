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


def _sync_articles():
    newara_articles = []

    ara_cursor.execute(query=read_queries['articles'] .format(100))
    articles = ara_cursor.fetchall()

    print(datetime.now(), 'article fetch finished')

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
                newara_articles.append(tuple(parsed.values()))

    print(datetime.now(), 'ready for execution')

    newara_cursor.executemany(write_queries['core_article'], newara_articles)
    newara_db.commit()

def _sync_comments():
    newara_comments = []

    ara_cursor.execute(query=read_queries['articles'].format(100))
    articles = ara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['core_article'].format(100))
    new_articles = newara_cursor.fetchall()
    ara_cursor.execute(query=read_queries['files'].format(100))
    files = ara_cursor.fetchall()

    print(datetime.now(), 'comment fetch finished')

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

    print(datetime.now(), 'ready for execution')
    newara_cursor.executemany(write_queries['core_comment'], newara_comments)
    newara_db.commit()

def get_attachment_id(files, article_id):
    for file in files:
        if file['article_id'] == article_id:
            return file[id]
    return None

def get_parent_article_id(new_articles, root_id):
    for article in new_articles:
        if article['id'] == root_id:
            return article['id']
    return None

def sync():
    _sync_articles()
    _sync_comments()
    print(datetime.now(), 'insertion finished')
