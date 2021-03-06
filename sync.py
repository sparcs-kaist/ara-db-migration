from datetime import datetime, timedelta
from tqdm import tqdm

import boto3 as boto3
import bs4 as bs4
from botocore.exceptions import ClientError

from mysql import ara_cursor, newara_middle_cursor, newara_middle_db
from query import read_queries, write_queries


s3 = boto3.resource('s3')
client = boto3.client('s3')


def _get_s3_object(key):
    try:
        obj = s3.ObjectSummary('sparcs-newara', key).get()
        size = obj['ContentLength']
        content_type = obj['ContentType']
        return {'size': size, 'content_type': content_type}
    except ClientError:
        print(f'File not exist in s3: {key}')
        return None


def _match_board_and_topic(ara_board, ara_heading):
    board_and_heading = {
        42: (2, 6),
        41: (2, 5),
        39: (2, 2),
        12: (2, 8),
        11: (2, 3),
        10: (2, 9),
        9: (2, 4),
        8: (2, 1),
        4: (7, 13),
        1: (7, None),
        2: (7, None),
        3: (7, None),
        5: (7, None),
        6: (7, None),
        7: (7, None),
        13: (3, 18),
        30: (2, None),
        34: (7, 10),
        33: (7, 10),
        14: (7, None),
        15: (7, None),
        16: (7, None),
        17: (7, None),
        18: (7, None),
        19: (7, None),
        26: (7, 12),
        27: (7, 12),
        28: (7, 12),
        25: (7, 12),
        24: (7, 12),
        20: (4, None),
        21: (4, None),
        23: (6, None),
        22: (6, None),
        35: (3, None),
        36: (3, 16),
        37: (3, None),
        38: (3, None),
    }.get(ara_heading)

    if board_and_heading:
        return board_and_heading

    else:
        board_and_heading = {
            1: (2, None),
            2: (7, None),
            3: (5, None),
            5: (7, 11),
            8: (3, None),
            10: (7, None),
            17: (7, 10),
            29: (7, None),
            30: (7, 12),
            42: (4, None),
            43: (6, None),
            48: (7, None),
            49: (3, 16),
            51: (4, 20),
        }.get(ara_board)

    if board_and_heading:
        return board_and_heading

    else:
        return (None, None)


def _replace_enter(s):
    return s.replace('\r\n', '<br>').replace('\n', '<br>')


def _sync_articles(articles, auth_users_dict):
    newara_articles = []

    author_none = 0
    garbage_num = 0
    new_id_val = 1 # set new_id_val for consecutive id

    for article in tqdm(articles):
        if article['parent_id'] is None:
            try:
                author_id = auth_users_dict[article['author_id']]
            except KeyError:
                author_none += 1
                print('article id: ', article['id'], 'author id: ', article['author_id'])
                # author_id = None
            parsed = {
                'id': article['id'],
                'new_id': new_id_val,
                'created_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'updated_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'deleted_at': ((article['date'] - timedelta(hours=9)) if article['deleted'] else datetime.min).isoformat(),
                'title': article['title'],
                'content': _replace_enter(article['content']),
                'content_text': ' '.join(bs4.BeautifulSoup(article['content'], features='html5lib').find_all(text=True)),
                'is_anonymous': False,
                'is_content_sexual': False,
                'is_content_social': False,
                'hit_count': article['hit'],
                'migrated_hit_count': article['hit'],
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'migrated_positive_vote_count': article['positive_vote'],
                'migrated_negative_vote_count': article['negative_vote'],
                'commented_at': (article['last_reply_date'] - timedelta(hours=9)).isoformat(),
                'created_by_id': author_id,
                'parent_board_id': _match_board_and_topic(article['board_id'], article['heading_id'])[0],
                'parent_topic_id': _match_board_and_topic(article['board_id'], article['heading_id'])[1],
                'url': None,
                'comment_count': article['reply_count'],
                'content_updated_at': (article['date'] - timedelta(hours=9)).isoformat(),
            }

            if parsed['parent_board_id'] is not None:
                # print(article['id'])
                newara_articles.append(tuple(parsed.values()))
                new_id_val += 1

            else:
                garbage_num+=1

    print("garbage num {}" .format(garbage_num))
    print(datetime.now(), 'sync articles')
    print(author_none)

    newara_middle_cursor.executemany(write_queries['core_article'], newara_articles)
    newara_middle_db.commit()


def _sync_attachments(files, articles_dict):
    newara_files = []
    # set a consecutive id: new_id
    new_id_val = 1

    for f in tqdm(files):
        # print(f['article_id'])
        try:
            article = articles_dict[f['article_id']]
        except KeyError:
            article = None
        # article = get_article(articles, f['article_id'])
        if article:
            parsed = {
                'id': f['id'],
                'new_id': new_id_val,
                'created_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'updated_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'deleted_at': ((article['date'] - timedelta(hours=9)) if article['deleted'] else datetime.min).isoformat(),
                'file': 'ara-files/{}/{}'.format(f['filepath'], f['saved_filename']),
                'mimetype': 'migrated',
                'size': 0,
            }
            new_id_val += 1
            newara_files.append(tuple(parsed.values()))

    print(datetime.now(), 'sync attachment')
    newara_middle_cursor.executemany(write_queries['core_attachment'], newara_files)
    newara_middle_db.commit()


def _sync_article_attachments(new_articles_dict, files, file_id_to_newid_dict):
    newara_article_attachments = []

    fid = 1

    for f in tqdm(files):
        try:
            article = new_articles_dict[f['article_id']]
        except KeyError:
            # print("article none {} {}".format(f['article_id'], f['id']))
            # article을 전체를 옮기면 없어질 에러
            article = None
        # article = get_article(new_articles, f['article_id'])
        if article:
            # 여기서 두개다 new_id로 바꾸기
            parsed = {
                'id': fid,
                'article_id': article['id'],
                'attachment_id': file_id_to_newid_dict[f['id']],
            }
            newara_article_attachments.append(tuple(parsed.values()))
            fid += 1

    print(datetime.now(), 'sync article attachments')
    newara_middle_cursor.executemany(write_queries['core_article_attachments'], newara_article_attachments)
    newara_middle_db.commit()


def _sync_comments(articles, new_articles_dict, files_id_dict, auth_users_dict):
    newara_comments = []
    author_none = 0

    # set a consecutive id: new_id
    new_id_val = 1

    for article in tqdm(articles):
        if article['parent_id'] is not None and article['root_id'] == article['parent_id']:
            try:
                attachment_id = files_id_dict[article['id']]
            except KeyError:
                # 댓글에 첨부된 파일이 없는 경우
                attachment_id = None
            try:
                author_id = auth_users_dict[article['author_id']]
            except KeyError:
                author_none += 1
                print(article['author_id'])
                author_id = None
            try:
                parent_article = new_articles_dict[article['root_id']]
                parent_article_id = parent_article['id']
            except KeyError:
                # 아마도 migration 되지 않는 시삽에게 보내기 같은 글들에 대한 댓글
                parent_article_id = None

            if not parent_article_id: continue
            parsed = {
                'id': article['id'],
                'new_id': new_id_val,
                'created_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'updated_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'deleted_at': ((article['date'] - timedelta(hours=9)) if article['deleted'] else datetime.min).isoformat(),
                'content': article['content'],
                'is_anonymous': False,
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'attachment_id': attachment_id,
                'created_by_id': author_id,
                'parent_article_id': parent_article_id,
                'parent_comment_id': None,
            }
            new_id_val += 1

            newara_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'sync comments')
    print(author_none)
    newara_middle_cursor.executemany(write_queries['core_comment'], newara_comments)
    newara_middle_db.commit()
    return new_id_val


def _sync_co_comments(articles, new_articles_dict, new_comments, files_id_dict, auth_users_dict, new_id_val):
    newara_co_comments = []
    author_none = 0
    for article in tqdm(articles):
        if article['parent_id'] is not None and article['root_id'] != article['parent_id']:
            try:
                attachment_id = files_id_dict[article['id']]
            except KeyError:
                # 댓글에 첨부된 파일이 없는 경우
                attachment_id = None
            try:
                parent_article = new_articles_dict[article['root_id']]
                parent_article_id = parent_article['id']
            except KeyError:
                # 아마도 migration 되지 않는 시삽에게 보내기 같은 글들에 대한 댓글
                parent_article_id = None
            try:
                author_id = auth_users_dict[article['author_id']]
            except KeyError:
                author_none += 1
                author_id = None

            if not parent_article_id: continue
            parsed = {
                'id': article['id'],
                'new_id': new_id_val,
                'created_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'updated_at': (article['date'] - timedelta(hours=9)).isoformat(),
                'deleted_at': ((article['date'] - - timedelta(hours=9)) if article['deleted'] else datetime.min).isoformat(),
                'content': article['content'],
                'is_anonymous': False,
                'positive_vote_count': article['positive_vote'],
                'negative_vote_count': article['negative_vote'],
                'attachment_id': attachment_id,
                'created_by_id': author_id,
                # 'parent_article_id': get_parent_article_id(new_articles, article['root_id']),
                'parent_article_id': parent_article_id,
                'parent_comment_id': get_parent_comment_id(new_comments, newara_co_comments, article['root_id'], article['parent_id']),
            }
            new_id_val += 1

            newara_co_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'sync cocomments')
    print(author_none)
    newara_middle_cursor.executemany(write_queries['core_comment'], newara_co_comments)
    newara_middle_db.commit()


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
            return newara_co_comment[12] # parent comment id
    return None


def sync():
    FETCH_NUM = 600000
    print("{} articles fetch" .format(FETCH_NUM))

    ara_cursor.execute(query=read_queries['files'] .format(FETCH_NUM))
    files = ara_cursor.fetchall()
    ara_cursor.execute(query=read_queries['articles'] .format(FETCH_NUM))
    articles = ara_cursor.fetchall()

    newara_middle_cursor.execute(query=read_queries['auth_user'].format(80000))
    auth_users = newara_middle_cursor.fetchall()

    articles_dict = {}
    for article in articles:
        articles_dict[article['id']] = article

    files_id_dict = {}
    for f in files:
        files_id_dict[f['article_id']] = f['id']

    auth_users_dict = {}
    for au in auth_users:
        auth_users_dict[au['id']] = au['id']

    print("fetched files and articles")

    _sync_articles(articles, auth_users_dict)
    _sync_attachments(files, articles_dict)

    newara_middle_cursor.execute(query=read_queries['core_article'].format(FETCH_NUM))
    new_articles = newara_middle_cursor.fetchall()
    newara_middle_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    new_attachments = newara_middle_cursor.fetchall()

    new_articles_dict = {} # map old article id to new article id
    for new_article in new_articles:
        new_articles_dict[new_article['id']] = new_article

    file_id_to_newid_dict = {}  # map old attachment id to new attachment id
    for attachment in new_attachments:
        file_id_to_newid_dict[attachment['id']] = attachment['id']

    print('fetched core_article and core_attachment')

    _sync_article_attachments(new_articles_dict, files, file_id_to_newid_dict)
    next_comment_id = _sync_comments(articles, new_articles_dict, files_id_dict, auth_users_dict)

    newara_middle_cursor.execute(query=read_queries['core_comment'].format(FETCH_NUM))
    new_comments = newara_middle_cursor.fetchall()
    print('fetched core_comment')

    _sync_co_comments(articles, new_articles_dict, new_comments, files_id_dict, auth_users_dict, next_comment_id)

    print(datetime.now(), 'insertion finished')
