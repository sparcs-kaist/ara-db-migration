from datetime import datetime

# import boto3 as boto3
# import bs4 as bs4
# from botocore.exceptions import ClientError

from mysql import ara_cursor, newara_middle_cursor, newara_middle_db
from query import read_queries, write_queries


# s3 = boto3.resource('s3')
# client = boto3.client('s3')

def _sync_auth_user(users, miss_users):
    newara_auth_user = []

    for user in users:
        if user:
            if user['username'] == "??": username = "dup??"
            else: username = user['username']

            if not user['join_time']: join_time = datetime.now().isoformat()
            else: join_time = user['join_time'].isoformat()
            parsed = {
                'id': user['id'],
                'password': user['password'],
                'last_login': (user['last_login_time'] if user['last_login_time'] else datetime.min).isoformat(),
                'is_superuser': 0,
                'username': username or "__deleted__{}".format(user['id']),
                'first_name': "",
                'last_name': "",
                'email': user['email'] or '{}@noemail'.format(user['id']),
                'is_staff': user['is_sysop'],
                'is_active': 0,
                'date_joined': join_time,
            }

            newara_auth_user.append(tuple(parsed.values()))

    for mu in miss_users:
        parsed = {
            'id': mu,
            'password': 'youcannotlogin',
            'last_login': datetime.min.isoformat(),
            'is_superuser': 0,
            'username': "__deleted__{}".format(mu),
            'first_name': "",
            'last_name': "",
            'email': '{}@noemail'.format(mu),
            'is_staff': 0,
            'is_active': 0,
            'date_joined': datetime.min.isoformat(),
        }
        newara_auth_user.append(tuple(parsed.values()))

    print(datetime.now(), 'sync auth_user')
    newara_middle_cursor.executemany(write_queries['auth_user'], newara_auth_user)
    newara_middle_db.commit()


def _sync_user_userprofile(users, auth_users_dict, users_name_dict, miss_users):
    newara_user_userprofile = []
    dup = 1

    for user in users:
        # user_id = get_use_id(auth_users, user['id'])
        try:
            user_id = auth_users_dict[user['id']]
        except KeyError:
            print(user['id'])
            user_id = None

        if user_id:
            if not user['username'] and user['nickname'] == "탈퇴회원":
                nickname = "__deleted__empty_{}".format(dup)
                dup += 1
            elif "??" in user['username']:
                nickname = "empty_{}".format(dup)
                dup += 1
            else:
                nickname = user['username']

            if not user['join_time']: join_time = datetime.now().isoformat()
            else: join_time = user['join_time'].isoformat()
            parsed = {
                'created_at': join_time,
                'updated_at': join_time,
                'deleted_at': (user['last_login_time'] if user['deleted'] else datetime.min).isoformat(),
                'uid': None,
                'sid': None,
                'sso_user_info': "{}",
                'picture': "",
                'nickname': nickname,
                'see_sexual': 0,
                'see_social': 0,
                'extra_preferences': "{}",
                'user_id': user_id,
                'is_past': 1,
                'ara_id': user['username'] or "__deleted__{}".format(dup),
                'is_kaist': 0,
            }

            newara_user_userprofile.append(tuple(parsed.values()))

    for mu in miss_users:
        parsed = {
            'created_at': datetime.min.isoformat(),
            'updated_at': datetime.min.isoformat(),
            'deleted_at': datetime.min.isoformat(),
            'uid': None,
            'sid': None,
            'sso_user_info': "{}",
            'picture': "",
            'nickname': "empty_{}".format(mu),
            'see_sexual': 0,
            'see_social': 0,
            'extra_preferences': "{}",
            'user_id': mu,
            'is_past': 1,
            'ara_id': "__deleted__{}".format(dup),
            'is_kaist': 0,
        }
        newara_user_userprofile.append(tuple(parsed.values()))

    print(datetime.now(), 'sync user_userprofile')
    newara_middle_cursor.executemany(write_queries['user_userprofile'], newara_user_userprofile)
    newara_middle_db.commit()


def get_use_id(auth_users, user_id):
    for auth_user in auth_users:
        if auth_user['id'] == user_id:
            return auth_user['id']

def sync_users():
    FETCH_NUM = 80000

    ara_cursor.execute(query=read_queries['users'] .format(FETCH_NUM))
    users = ara_cursor.fetchall()

    miss_users = [65673, 69660]

    users_name_dict = {}
    # for u in users:
    #     if u['nickname'].lower() in users_name_dict and u['nickname'] != "탈퇴회원":
    #         users_name_dict[u['nickname'].lower()] = 1
    #     else:
    #         users_name_dict[u['nickname'].lower()] = 0

    _sync_auth_user(users, miss_users)

    newara_middle_cursor.execute(query=read_queries['auth_user'] .format(FETCH_NUM))
    auth_users = newara_middle_cursor.fetchall()

    auth_users_dict = {}
    for au in auth_users:
        auth_users_dict[au['id']] = au['id']

    _sync_user_userprofile(users, auth_users_dict, users_name_dict, miss_users)
    print(datetime.now(), 'users insertion finished')
