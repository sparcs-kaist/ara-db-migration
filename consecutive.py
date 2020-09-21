from datetime import datetime

from mysql import ara_cursor, newara_middle_cursor, newara_middle_db, newara_consecutive_cursor, newara_consecutive_db
from query import read_queries, write_queries
from tqdm import tqdm


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
            'picture': user['picture'],
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
        }
        newara_articles.append(tuple(parsed.values()))

    print(datetime.now(), 'sync articles')
    newara_consecutive_cursor.executemany(write_queries['core_article_consecutive'], newara_articles)
    newara_consecutive_db.commit()


# make attachment id consecutive and change 'file' from hash to actual file name
def _make_consecutive_attachment_id(attachments, files_hash_to_name_dict):
    newara_attachments = []

    # 같은 날에 올라온 attachment names 저장 (같은 날에 같은 이름의 파일들이 여러개 올라오면, 뒤에 1, 2, 3, ... 붙여주기 위함)
    current_date = ''
    current_date_attachments = []

    maxlen = 0
    maxlenstr = ''
    maxlenstrold = ''

    for att in tqdm(attachments):
        # parse file path
        path_list = att['file'].split('/')
        old_filename = files_hash_to_name_dict[path_list[5]].replace(' ', '_')
        new_name = old_filename
        separator = '.'

        # 날짜 트래킹 (같은 날짜의 첨부파일은 같은 폴더에 있으므로, 이름이 같을 시 바꿔주기 위해 같은 날짜의 파일들을 모아보기 위한 리스트 생성)
        # if new day, reset current_date_attachments list
        if current_date != path_list[4]:  # if beginning of new date
            current_date = path_list[4]  # update current date
            current_date_attachments = [old_filename]

        # if file with same name exists in current bucket, add '_i' to current file name (i=1,2,3,...)
        else:
            i = 1
            while new_name in current_date_attachments:
                name_list = old_filename.split('.')  # 끝에 .jpg, .pdf 등 확장자가 있는 경우를 위해
                name_list[0] = name_list[0] + f'({i})'
                new_name = separator.join(name_list)
                i = i + 1
            current_date_attachments.append(new_name)

        path_list[5] = new_name
        new_path = '/'.join(path_list)

        print('old: ', att['file'])
        print('new: ', new_path)

        parsed = {
            'id': att['new_id'],
            'created_at': att['created_at'],
            'updated_at': att['updated_at'],
            'deleted_at': att['deleted_at'],
            'file': new_path,
            'mimetype': att['mimetype'],
            'size': att['size'],
        }
        newara_attachments.append(tuple(parsed.values()))
        if maxlen < len(new_path):
            maxlen = len(new_path)
            maxlenstr = new_path
            maxlenstrold = att['file']

    print('maxlen: ', maxlen)
    print('maxlen str: ', maxlenstr)
    print('maxlen str old: ', maxlenstrold)
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

    # fetch attachment hash and attachment name from original aradump db
    # with original ara db, create a dictionary of (key: file hash, val: filename)
    ara_cursor.execute(query=read_queries['files'].format(FETCH_NUM))
    files = ara_cursor.fetchall()
    files_hash_to_name_dict = {}
    for f in files:
        files_hash_to_name_dict[f['saved_filename']] = f['filename']

    newara_middle_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    core_attachments = newara_middle_cursor.fetchall()
    _make_consecutive_attachment_id(core_attachments, files_hash_to_name_dict)
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
