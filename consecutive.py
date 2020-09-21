import random
from datetime import datetime

from mysql import newara_middle_cursor, newara_middle_db, newara_consecutive_cursor, newara_consecutive_db
from query import read_queries, write_queries


def _make_consecutive_auth_user_id(users):
    newara_auth_user = []

    for user in users:
        parsed = {
            'id': user['new_id'],
            'password': user['password'],
            'last_login': user['last_login'],
            'is_superuser': user['is_superuser'],
            'username': user['username'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'is_staff': user['is_staff'],
            'is_active': user['is_active'],
            'date_joined': user['date_joined'],
        }

        newara_auth_user.append(tuple(parsed.values()))

    print(datetime.now(), 'make consecutive auth_user')
    newara_consecutive_cursor.executemany(write_queries['auth_user_consecutive'], newara_auth_user)
    newara_consecutive_db.commit()


def _make_random_profile_picture() -> str:
    colors = ['blue', 'red', 'gray']
    numbers = ['1', '2', '3']

    temp_color = random.choice(colors)
    temp_num = random.choice(numbers)
    default_picture = f'user_profiles/default_pictures/{temp_color}-default{temp_num}.png'

    return default_picture


def _make_consecutive_user_userprofile_id(users):
    newara_user_userprofile = []

    for user in users:
        parsed = {
            'created_at': user['created_at'],
            'updated_at': user['updated_at'],
            'deleted_at': user['deleted_at'],
            'uid': user['uid'],
            'sid': user['sid'],
            'sso_user_info': user['sso_user_info'],
            'picture': user['picture'] or _make_random_profile_picture(),
            'nickname': user['nickname'],
            'nickname_updated_at': user['nickname_updated_at'],
            'see_sexual': user['see_sexual'],
            'see_social': user['see_social'],
            'extra_preferences': user['extra_preferences'],
            'user_id': user['new_id'],
            'is_newara': user['is_newara'],
            'ara_id': user['ara_id'],
            'group': user['group'],
        }

        newara_user_userprofile.append(tuple(parsed.values()))

    print(datetime.now(), 'make consecutive user_userprofile')
    newara_consecutive_cursor.executemany(write_queries['user_userprofile_consecutive'], newara_user_userprofile)
    newara_consecutive_db.commit()


def _make_consecutive_article_id(articles, user_id_to_newid_dict):
    newara_articles = []

    for article in articles:
        parsed = {
            'id': article['new_id'],
            'created_at': article['created_at'],
            'updated_at': article['updated_at'],
            'deleted_at': article['deleted_at'],
            'title': article['title'],
            'content': article['content'],
            'content_text': article['content_text'],
            'is_anonymous': article['is_anonymous'],
            'is_content_sexual': article['is_content_sexual'],
            'is_content_social': article['is_content_social'],
            'hit_count': article['hit_count'],
            'positive_vote_count': article['positive_vote_count'],
            'negative_vote_count': article['negative_vote_count'],
            'commented_at': article['commented_at'],
            'created_by_id': user_id_to_newid_dict[article['created_by_id']],
            'parent_board_id': article['parent_board_id'],
            'parent_topic_id': article['parent_topic_id'],
            'url': article['url'],
            'migrated_hit_count': article['hit_count'],
            'migrated_positive_vote_count': article['positive_vote_count'],
            'migrated_negative_vote_count': article['negative_vote_count'],
        }
        newara_articles.append(tuple(parsed.values()))

    print(datetime.now(), 'sync articles')
    newara_consecutive_cursor.executemany(write_queries['core_article_consecutive'], newara_articles)
    newara_consecutive_db.commit()


def _make_consecutive_attachment_id(attachments):
    newara_attachments = []

    for att in attachments:
        parsed = {
            'id': att['new_id'],
            'created_at': att['created_at'],
            'updated_at': att['updated_at'],
            'deleted_at': att['deleted_at'],
            'file': att['file'],
            'mimetype': att['mimetype'],
            'size': att['size'],
        }
        newara_attachments.append(tuple(parsed.values()))

    print(datetime.now(), 'make consecutive attachment')
    newara_consecutive_cursor.executemany(write_queries['core_attachment_consecutive'], newara_attachments)
    newara_consecutive_db.commit()


def _make_consecutive_article_attachments_id(core_article_attachments, article_id_to_newid_dict, attachment_id_to_newid_dict):
    newara_article_attachments = []

    for a in core_article_attachments:
        old_article_id = a['article_id']
        old_attachment_id = a['attachment_id']

        parsed = {
            'id': a['id'],
            'article_id': article_id_to_newid_dict[old_article_id],
            'attachment_id': attachment_id_to_newid_dict[old_attachment_id],
        }

        newara_article_attachments.append(tuple(parsed.values()))

    print(datetime.now(), 'make consecutive article attachments')
    newara_consecutive_cursor.executemany(write_queries['core_article_attachments'], newara_article_attachments)
    newara_consecutive_db.commit()


def _make_consecutive_comments_id(comments, user_id_to_newid_dict, article_id_to_newid_dict, attach_id_to_newid_dict, comment_id_to_newid_dict):
    newara_comments = []

    for c in comments:
        new_attachment_id = None
        new_parent_article_id = None
        new_parent_comment_id = None

        if c['attachment_id']:
            new_attachment_id = attach_id_to_newid_dict[c['attachment_id']]
        if c['parent_article_id']:
            new_parent_article_id = article_id_to_newid_dict[c['parent_article_id']]
        if c['parent_comment_id']:
            new_parent_comment_id = comment_id_to_newid_dict[c['parent_comment_id']]

        parsed = {
            'id': c['new_id'],
            'created_at': c['created_at'],
            'updated_at': c['updated_at'],
            'deleted_at': c['deleted_at'],
            'content': c['content'],
            'is_anonymous': c['is_anonymous'],
            'positive_vote_count': c['positive_vote_count'],
            'negative_vote_count': c['negative_vote_count'],
            'attachment_id': new_attachment_id,
            'created_by_id': user_id_to_newid_dict[c['created_by_id']],
            'parent_article_id': new_parent_article_id,
            'parent_comment_id': new_parent_comment_id,
        }

        newara_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'make consecutive comments')
    newara_consecutive_cursor.executemany(write_queries['core_comment_consecutive'], newara_comments)
    newara_consecutive_db.commit()


def make_consecutive_id():
    # make users consecutive
    FETCH_NUM = 80000
    newara_middle_cursor.execute(query=read_queries['auth_user'] .format(FETCH_NUM))
    auth_users = newara_middle_cursor.fetchall()

    user_id_to_newid_dict = {}
    for au in auth_users:
        user_id_to_newid_dict[au['id']] = au['new_id']

    _make_consecutive_auth_user_id(auth_users)

    newara_middle_cursor.execute(query=read_queries['user_userprofile'].format(FETCH_NUM))
    user_userprofiles = newara_middle_cursor.fetchall()

    _make_consecutive_user_userprofile_id(user_userprofiles)

    print(datetime.now(), 'user id modification finished')

    # make articles, attachments, and comments consecutive
    FETCH_NUM = 600000

    newara_middle_cursor.execute(query=read_queries['core_article'].format(FETCH_NUM))
    core_articles = newara_middle_cursor.fetchall()
    _make_consecutive_article_id(core_articles, user_id_to_newid_dict)
    print(datetime.now(), 'article id modification finished')

    newara_middle_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    core_attachments = newara_middle_cursor.fetchall()
    _make_consecutive_attachment_id(core_attachments)
    print(datetime.now(), 'attachment id modification finished')

    newara_middle_cursor.execute(query=read_queries['core_article_attachments'].format(FETCH_NUM))
    core_article_attachments = newara_middle_cursor.fetchall()

    article_id_to_newid_dict = {}
    for a in core_articles:
        article_id_to_newid_dict[a['id']] = a['new_id']

    attach_id_to_newid_dict = {}
    for att in core_attachments:
        attach_id_to_newid_dict[att['id']] = att['new_id']

    _make_consecutive_article_attachments_id(core_article_attachments, article_id_to_newid_dict, attach_id_to_newid_dict)
    print(datetime.now(), 'article attachments id modification finished')

    newara_middle_cursor.execute(query=read_queries['core_comment'].format(FETCH_NUM))
    core_comment = newara_middle_cursor.fetchall()
    comment_id_to_newid_dict = {}
    for c in core_comment:
        comment_id_to_newid_dict[c['id']] = c['new_id']

    _make_consecutive_comments_id(core_comment, user_id_to_newid_dict, article_id_to_newid_dict, attach_id_to_newid_dict, comment_id_to_newid_dict)
    print(datetime.now(), 'comment id modification finished')

    print(datetime.now(), 'finish db migration :)')
