from datetime import datetime

# import boto3 as boto3
# import bs4 as bs4
# from botocore.exceptions import ClientError

from mysql import ara_cursor, newara_cursor, newara_db
from query import read_queries, write_queries


# s3 = boto3.resource('s3')
# client = boto3.client('s3')

def _sync_auth_user():
    newara_auth_user = []

    ara_cursor.execute(query=read_queries['users'] .format(100))
    users = ara_cursor.fetchall()

    for user in users:
        if user:
            parsed = {
                'id': user['id'],
                'password': user['password'],
                'last_login': (user['last_login_time'] if user['last_login_time'] else datetime.min).isoformat(),
                'is_superuser': 0,
                'username': user['username'],
                'first_name': "",
                'last_name': "",
                'email': user['email'],
                'is_staff': user['is_sysop'],
                'is_active': user['activated'],
                'date_joined': user['join_time'].isoformat(),
            }
            
            newara_auth_user.append(tuple(parsed.values()))


    print(datetime.now(), 'sync auth_user')
    newara_cursor.executemany(write_queries['auth_user'], newara_auth_user)
    newara_db.commit()


def _sync_user_userprofile():
    newara_user_userprofile = []

    ara_cursor.execute(query=read_queries['users'] .format(100))
    users = ara_cursor.fetchall()
    newara_cursor.execute(query=read_queries['auth_user'] .format(100))
    auth_users = newara_cursor.fetchall()

    for user in users:
        user_id = get_use_id(auth_users, user['id'])
        if user_id:
            parsed = {
                'created_at': user['join_time'].isoformat(),
                'updated_at': datetime.min.isoformat(),
                'deleted_at': (user['last_login_time'] if user['deleted'] else datetime.min).isoformat(),
                'uid': None,
                'sid': None,
                'sso_user_info': "{}",
                'picture': None,
                'nickname': user['nickname'],
                'see_sexual': 0,
                'see_social': 0,
                'extra_preferences': "{}",
                'user_id': user_id,
                'past_user': 1,
            }

            newara_user_userprofile.append(tuple(parsed.values()))


    print(datetime.now(), 'sync user_userprofile')
    newara_cursor.executemany(write_queries['user_userprofile'], newara_user_userprofile)
    newara_db.commit()


def get_use_id(auth_users, user_id):
    for auth_user in auth_users:
        if auth_user['id'] == user_id:
            return auth_user['id']

def sync_users():
    _sync_auth_user()
    _sync_user_userprofile()
    print(datetime.now(), 'users insertion finished')
