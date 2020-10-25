# 기존 디비에서 attachment name을 해시가 아닌 파일 이름으로 만들고, S3의 상응하는 파일 이름도 해시가 아닌 파일 이름으로 바꾸기 위한 코드입니다.
from datetime import datetime
from mysql import ara_cursor, newara_middle_cursor
from query import read_queries, write_queries, update_queries
from tqdm import tqdm
import boto3 as boto3
from botocore.exceptions import ClientError


def _rename_attachments(attachments, files_hash_to_name_dict):

    attachment_oldkey_to_newkey_dict = {}

    # 같은 날에 올라온 attachment names 저장 (같은 날에 같은 이름의 파일들이 여러개 올라오면, 뒤에 1, 2, 3, ... 붙여주기 위함)
    current_date = ''
    current_date_attachments = []
    maxlen = 0
    maxlenstr = ''

    for att in tqdm(attachments):
        # parse file path
        path_list = att['file'].split('/')
        old_filename = files_hash_to_name_dict[path_list[5]].replace(' ', '_')
        new_name = old_filename
        separator = '.'

        # 날짜 트래킹 (같은 날짜의 첨부파일은 같은 폴더에 있으므로, 이름이 같을 시 바꿔주기 위해 같은 날짜의 파일들을 모아보기 위한 리스트 생성)
        # if new day, reset current_date_attachments list
        if current_date != path_list[4]:                         # if beginning of new date
            current_date = path_list[4]                          # update current date
            current_date_attachments = [old_filename]

        # if file with same name exists in current bucket, add '_i' to current file name (i=1,2,3,...)
        else:
            i = 1
            while new_name in current_date_attachments:
                name_list = old_filename.split('.') # 끝에 .jpg, .pdf 등 확장자가 있는 경우를 위해
                name_list[0] = name_list[0] + f'({i})'
                new_name = separator.join(name_list)
                i = i + 1
                print(new_name)
            current_date_attachments.append(new_name)

        path_list[5] = new_name
        new_path = '/'.join(path_list)

        attachment_oldkey_to_newkey_dict[att['file']] = new_path

        print('new path: ', new_path)
        if maxlen < len(new_path):
            maxlen = len(new_path)
            maxlenstr = new_path

    # update values
    print(datetime.now(), 'finish renaming attachments in db')
    print('maxlen: ', maxlen)
    print('maxlen str: ', maxlenstr)

    return attachment_oldkey_to_newkey_dict


def change_attachment_name_in_s3():
    FETCH_NUM = 600000
    print("{} articles fetch".format(FETCH_NUM))

    # with original ara db, create a dictionary of (key: file hash, val: filename)
    ara_cursor.execute(query=read_queries['files'].format(FETCH_NUM))
    files = ara_cursor.fetchall()
    files_hash_to_name_dict = {}
    for f in files:
        files_hash_to_name_dict[f['saved_filename']] = f['filename']

    # rename attachments in newara db (from file hash to filename)
    newara_middle_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    core_attachments = newara_middle_cursor.fetchall()
    attachment_oldkey_to_newkey_dict = _rename_attachments(core_attachments, files_hash_to_name_dict)

    s3 = boto3.resource('s3')
    client = boto3.client('s3')

    # rename files in s3
    for key, value in tqdm(attachment_oldkey_to_newkey_dict.items()):
        print('key: ', key, '    value: ', value)
        try:
            s3.Object('sparcs-newara', value).copy_from(CopySource=f'sparcs-newara/{key}')
            s3.Object('sparcs-newara', key).delete()
        except ClientError:
            print(f'File not exist in s3: {key}')
            pass

