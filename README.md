# ara-db-migration 가이드

# 1. DB 생성
new-ara-api 레포의 Makefile을 이용해서 MySQL DB를 2개 생성해줍니다.

1. 첫번째 디비는 기존의 비연속적인 id를 연속적으로 만들기 위해서, 옮겨지는 테이블에 new_id라는 int column이 추가된 임시 DB입니다.

a) new-ara-api의 Makefile에서, init: 을 다음과 같이 변경해줍니다.

```
init:
	mysql -u root -e 'CREATE DATABASE new_ara_migration CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'
	python manage.py migrate
```

b) new-ara-api 디렉토리에서 `$ make init`을 실행하여 new_ara_migration DB 생성

c) datagrip에서, 생성된 new_ara_migration DB에서 다음 5개의 테이블에 new_id라는 int 칼럼을 추가합니다.
- auth_user
- core_article
- core_attachment
- core_comment
- user_userprofile

2. 두번째 디비는, 서비스에서 사용할 디비입니다. (기존에 비연속적이었던 id들이 연속적으로 매핑된 디비입니다)

a) new-ara-api의 Makefile에서, init: 을 다음과 같이 변경해줍니다.
```
init:
	mysql -u root -e 'CREATE DATABASE new_ara_consecutive CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'
	python manage.py migrate
```
b) new-ara-api 디렉토리에서 `$ make init`을 실행하여 new_ara_consecutive DB 생성

c) 여기까지 마치고 나면, Makefile의 init:을 원래 상태로 되돌려줍니다:
```
init:
	mysql -u root -e 'CREATE DATABASE new_ara CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;'
	python manage.py migrate
```
d) 생성된 2개의 db 둘다, core_board 안에 게시판 정보를 넣어줍니다 (아래 sql문을 실행해주면 됩니다)
```
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (1, '2020-04-05 01:48:21.783681', '0001-01-01 00:00:00', '0001-01-01 00:00:00', 'portal-notice', '포탈공지', 'portal notice', '포탈공지', 'portal notice', 1, 2, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (2, '2020-04-05 01:48:51.336389', '0001-01-01 00:00:00', '0001-01-01 00:00:00', 'organization-notice', '학생공지', 'organization notice', '학생단체', 'organization notice', 0, 2, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (3, '2020-09-01 07:29:46.471271', '2020-09-01 07:29:46.471313', '0001-01-01 00:00:00', 'wanted', 'Wanted', 'Wanted', 'Wanted', 'Wanted', 0, 2, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (4, '2020-09-01 07:30:25.884216', '2020-09-01 07:30:25.884273', '0001-01-01 00:00:00', 'market', '장터', 'Market', '장터', 'Market', 0, 2, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (5, '2020-09-01 07:36:40.279773', '2020-09-01 07:36:40.279830', '0001-01-01 00:00:00', 'food', '식사이야기', 'Food', '식사이야기', 'Food', 0, 6, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (6, '2020-09-01 07:37:07.467017', '2020-09-01 07:37:07.467076', '0001-01-01 00:00:00', 'qa', 'Q&A', 'Q&A', 'Q&A', 'Q&A', 0, 2, 0);
INSERT INTO core_board (id, created_at, updated_at, deleted_at, slug, ko_name, en_name, ko_description, en_description, is_readonly, access_mask, is_hidden) VALUES (7, '2020-09-01 07:37:47.576955', '2020-09-01 07:37:47.577012', '0001-01-01 00:00:00', 'talk', '자유게시판', 'Talk', '자유게시판', 'Talk', 0, 2, 0);

select * from core_board;

```

# 2. 코드 수정
ara-db-migration에서, 다음 부분들을 수정해주어야합니다.

1. (필수) relink.py -> 기존 게시물/코멘트에서, ara.kaist.ac.kr 링크들을 뉴아라 링크로 바꿔줍니다

relink.py 윗부분에, 뉴아라 링크를 `NEWARA_LINK = 'https://newara.dev.sparcs.org/'`로 넣어놓았습니다.
이 링크를 배포용 링크로 바꾼 후 실행해주셔야합니다. (링크 맨 뒤에 '/' 꼭 넣어주세요!)

2. (권장) sync_users.py, sync.py, consecutive.py, relink.py 등에서, 쿼리시 가져오는 갯수를 FETCH_NUM으로 제한하는데, 이 숫자들이 upperbound가 맞는지 확인하여야 합니다.

쿼리마다 `FETCH_NUM=60000` 등으로 제한하고 있습니다. 이 때, 실제 데이터의 갯수는 58000 등으로 조금 아슬아슬하게 상한값 이하였던 경우가 있습니다.

혹시라도 그 사이에 데이터가 많이 추가되어 상한값을 넘기는 경우가 있는지 확인할 필요가 있습니다.

그래서 migration 진행하기 전에, 각 쿼리에 적용되는 FETCH_NUM이 데이터의 실제 수보다 큰지 확인하면 좋을 것 같습니다.

3. (권장) 알 수 없는 오류로 (기존 DB에서 데이터가 이상해서) migration 불가한 사용자들 확인

sync_users.py에서 sync_user() 함수를 보시면, `miss_users = [65673, 69660, 81408]`라는 부분이 있습니다.

기존 ara DB에서 위 id를 가지신 세 사용자 분들은, 어떤 데이터 오류로 인해서 migration이 되지 않으시는 분들입니다.

제가 코드를 돌렸을 때 기준으로 (8/31 아라 DB로 돌렸습니다) 저렇게 세 분이 migration 되지 않았는데, 혹시라도 그 사이에 가입하신 분들 중에 다시 이런 경우가 있을 수도 있으니 확인하여야 합니다.

만약 sync_users.py가 에러없이 실행된다면, 위의 세 분만 데이터 오류가 있는 것으로, 수정 없이 진행하시면 됩니다.

하지만 혹시 오류가 난다면, 새로운 사용자들 중 데이터가 훼손된 분들이 있을 가능성이 있습니다. 이 경우, 이 분의 id를 위 리스트에 추가하셔야 합니다. 

4. (추후 업데이트 필요) 혹시 S3에 있는 파일이름을 해시에서 파일 이름으로 바꾸는 작업을 한 번 더 해야된다면, 수정할 것이 더 생길 것 같습니다 

(S3 파일이름을 변경함과 동시에, 그 첨부파일과 매핑된 core_attachment object의 이름을 변경하면서, 매핑이 유지되도록 해야되기 때문에 실행 순서에 주의해야될 것 같습니다. 
혹시 S3의 첨부파일들의 이름을 다시 변경해야한다면, 제게 말씀해주시면 실행 순서를 고민해서 글을 업데이트하겠습니다)

5. (필수) 혹시 기존 게시판 이름 -> 새로운 게시판 이름의 매핑중에 변경된 것이 있다면, 그에 맞추어 relink.py의 old_board_name_to_new_name와 sync.py의 _match_board_and_topic를 변경해주어야합니다.

# 3. 코드 실행

이 디렉토리의 main.py내의 main() 함수를 실행시킵니다.

각 함수의 역할은 다음과 같습니다.

```
def main():
    print(datetime.now(), 'main start')
    start = time.time()
    sync_users() # ara_dump에서 사용자들을 가져와, new_id (연속적 id)를 추가해서 new_ara_migration DB에 넣어줍니다.
    sync() # ara_dump에서 게시글, 댓글, 대댓글, 첨부파일을 가져와, new_id (연속적 id)를 추가해서 new_ara_migration DB에 넣어줍니다.
    make_consecutive_id() # new_ara_migration DB를 그대로 new_ara_consecutive DB에 넣어주면서, 기존의 (비연속적인) id 값들을 (연속적인) new_id 값들로 대체해서 저장합니다.
    update_ara_links() # 게시글과 댓글에서, ara.kaist.ac.kr로 작성된 링크들을, 뉴아라 링크로 바꿔줍니다. -> 예외케이스가 많아서, 빨간 exception 메세지들이 많이 뜨는데 정상작동 맞습니다.
    end = time.time()
    print("Migration took {} seconds".format(end-start))

```

이론적으로는, 한번에 되어야하는데, 제 경험상 (제가 아직 부족해서ㅠㅠ) 예상치 못한 케이스들로 중단에 멈추는 경우가 많았어요.

8/31 ara_dump 기준으로는 현재 위 코드가 연속적으로 다 돌아가야하지만, 그 사이 올라온 글들 / 가입한 사용자들 중에 또 예상치 못한 예외 케이스가 생겼을 경우 처음부터 끝까지 스무스하게 진행되지 않을 수도 있습니다.

그래서 조심스럽게 추천드리자면, main 함수에서 sync_users(), sync(), make_consecutive_id(), update_ara_links()를 한번에 한줄씩 실행하는 것도 좋은 방법 같습니다.

부족한 코드이기에, 혹시 이상한 부분이나, 이상한 에러 등 문제가 발생할 경우 연락 주시면 최대한 빠르게 해결하도록 노력하겠습니다.


# 4. 예상되는 문제점
- AWS credentials

AWS 계정이 두 부분에서 필요합니다.

1. S3에서 첨부파일들의 용량을 가져올 때 (sync() 내에서 실행)

2. S3에서 첨부파일들의 이름을, 해시에서 파일이름으로 바꿀 때 (filename 브랜치의 change_attachment_name.py에 정의되어 있는 함수입니다. 현재 master에 merge되진 않았습니다. 

이건 이미 한번 실행되었기 때문에, 다시 실행할 필요가 있는지 잘 모르겠습니다. 만약 다시 실행되어야한다면, 함수 실행 순서에 주의하여야합니다. s3 첨부파일의 이름을 바꾸는 부분은 필요 시 추후 작성해서 업겠습니다.)

제 컴퓨터에서 실행했을 때는, 로컬에 AWS credentials가 설정이 되어있었음에도 불구하고 어떤 이유로인지(?) 함수 실행 중에 AWS 계정 정보를 찾지 못하였습니다.

그 당시에 코드를 돌리는 것이 급해서, 급한대로 (안 좋은 방법인 것을 알면서도) 코드 내에 AWS credentials를 하드코딩해서 넣고, 실행 후 AWS credentials를 삭제하였습니다. 

(당연히 이 글을 읽으시는 분께 이 방법은 추천드리고 싶지 않습니다)

제 경우에 안된 것을 보니 제가 코드 내에서 AWS 계정 정보를 불러오는 과정에서 무엇인가 실수했을 가능성도 있습니다.

제가 해결하지 못한 문제라서 확실한 해결책을 드릴 수 없어 죄송합니다.

이 코드를 실행하시는 분께서는, AWS credentials가 문제 없이 해결되었으면 좋겠지만, 혹시라도 제 코드 상 무언가의 실수로 AWS credentials를 로컬에서 읽어오지 못한다면, 그 부분을 수정해서 커밋해주시면 정말 감사할 것 같습니다!


# 5. 예상 시간

맥북프로 13인치 2017 (2.3 GHz i5, 메모리 8GB) 기준으로 대략 5~6시간 정도 걸린 것으로 기억합니다.

특히 오래 걸리는 부분은 다음 4가지입니다: 
1) 게시글 옮겨오는 부분 (sync() 내에서 실행)
2) 댓글 옮겨오는 부분 (sync() 내에서 실행)
3) s3에서 첨부파일 각각의 용량을 가져오는 부분 (sync() 내에서 실행)
4) 게시글/댓글에서, ara 기반 링크를 new ara 링크들로 바꿔주는 작업 (update_ara_links() 내에서 실행)

