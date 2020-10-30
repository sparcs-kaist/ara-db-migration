from datetime import datetime

from mysql import ara_cursor, newara_middle_cursor, newara_middle_db, newara_consecutive_cursor, newara_consecutive_db
from query import read_queries, write_queries, update_queries
from tqdm import tqdm


NEWARA_LINK = 'newara.sparcs.org'

corner_cases = [] # cases that cannot be changed to NEWARA_LINK

article_id_to_newid_dict = {}
attachment_id_to_path_dict = {}
comment_id_to_newid_dict = {}
comment_get_parent_article_id = {}

old_board_name_to_new_name = {
    'notice': 'portal-notice',
    'garbages': 'talk',
    'food': 'food',
    'love': 'talk',
    'wanted': 'wanted',
    'infoworld': 'talk',
    'lostfound': 'talk',
    'hobby': 'talk',
    'siggame': 'talk',
    'buysell': 'market',
    'qanda': 'qa',
    'funlife': 'talk',
    'jobs': 'wanted',
    'housing': 'market',
}


def relink_articles(articles_with_links):
    newara_articles = []

    for article in tqdm(articles_with_links):
        parsed = {
            'content': replace_link(article['content']),
            'content_text': replace_link(article['content_text']),
            'id': article['id'],
        }
        newara_articles.append(tuple(parsed.values()))

    # update values
    print(datetime.now(), 'relink articles')
    newara_consecutive_cursor.executemany(update_queries['core_article_content'], newara_articles)
    newara_consecutive_db.commit()


def relink_comments(comments_with_links):
    newara_comments = []

    for c in tqdm(comments_with_links):
        parsed = {
            'content': replace_link(c['content']),
            'id': c['id'],
        }
        newara_comments.append(tuple(parsed.values()))

    print(datetime.now(), 'relink comments')
    newara_consecutive_cursor.executemany(update_queries['core_comment_content'], newara_comments)
    newara_consecutive_db.commit()


# returns string, with the old link replaced with the new link
def replace_link(content_str):
    link_begin_pos = content_str.find('ara.kaist.ac.kr/', 0, -1)

    # termination condition for recursion
    if link_begin_pos == -1:
        return content_str

    # identify possible end of link with " " or "\n" or ")"
    link_end1 = content_str.find('\n', link_begin_pos)
    link_end2 = content_str.find(' ', link_begin_pos)
    link_end3 = content_str.find(')', link_begin_pos)
    link_end4 = content_str.find('"', link_begin_pos)
    link_end5 = content_str.find('\r', link_begin_pos)
    link_end6 = content_str.find('을', link_begin_pos)
    link_end7 = content_str.find('로', link_begin_pos)
    link_end8 = content_str.find('<', link_begin_pos)
    link_end9 = content_str.find('.<', link_begin_pos)

    if link_end1 == -1:
        link_end1 = 1000000
    if link_end2 == -1:
        link_end2 = 1000000
    if link_end3 == -1:
        link_end3 = 1000000
    if link_end4 == -1:
        link_end4 = 1000000
    if link_end5 == -1:
        link_end5 = 1000000
    if link_end6 == -1:
        link_end6 = 1000000
    if link_end7 == -1:
        link_end7 = 1000000
    if link_end8 == -1:
        link_end8 = 1000000
    if link_end9 == -1:
        link_end9 = 1000000

    # identify which candidate is end of link
    link_end_pos = min((link_end1, link_end2, link_end3, link_end4, link_end5, link_end6, link_end7, link_end8, link_end9))

    if link_end_pos == 1000000:
        link_end_pos = len(content_str)

    old_link = content_str[link_begin_pos:link_end_pos]

    # returns path list
    path = old_link.lower().split('/')

    # remove 'mobile' from link
    if (path[1] == 'mobile') or (path[1] == 'm'):
        del path[1]

    if path[-1] == '':
        del path[-1]

    # case 1: variation of ara's main page (ex. mobile main page: ara.kaist.ac.kr/mobile/)
    # (주로 옛날에 모바일 페이지 테스트하는 링크들이라서 새 링크로 바꿀 필요가 없음)
    if len(path) == 1:
        return content_str

    # case 2: link is board, post, attachment file, or query on a board
    elif path[1] == 'board':
        # case 2-a: link is a board
        if len(path) < 4:
            try:
                new_board_name = old_board_name_to_new_name[path[2]]

            except KeyError: # if this board no longer exists, return original link
                corner_cases.append(old_link)
                return content_str

            new_link = NEWARA_LINK + new_board_name
            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-b: link is a file
        if 'file' in path:
            file_index = path.index('file')
            old_attachment_id = int(path[file_index + 1])
            attachment_path = attachment_id_to_path_dict[old_attachment_id]
            new_link = 'https://sparcs-newara.s3.amazonaws.com/ara-' + attachment_path
            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-c: link is write page
        elif path[3] == 'write':
            new_link = NEWARA_LINK + 'write'
            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-d: link is query on a board
        elif path[3] == 'search':
            search_word_pos = path[4].find('search_word=') + 12
            search_word = path[4][search_word_pos:]

            # check if this query is made to a valid board. If not valid board, query on all boards
            try:
                new_board_name = old_board_name_to_new_name[path[2]]
                new_link = NEWARA_LINK + 'board/' + new_board_name + '?query=' + search_word

            except KeyError: # if this board no longer exists, return original link
                new_link = NEWARA_LINK + 'board?query=' + search_word

            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-e: link to a post: contains board/{boardName}/{articleID}
        else:
            try:
                old_id = int(path[3].split('#')[0])
                new_article_id = article_id_to_newid_dict.get(old_id, None)
                if new_article_id is None: # this link is a comment. Change old link to new link of parent article
                    new_comment_id = comment_id_to_newid_dict[old_id]
                    new_article_id = comment_get_parent_article_id[new_comment_id]

            # KeyError: unable to index article/comment
            # ValueError: value in link is not a number
            except (KeyError, ValueError):
                corner_cases.append(old_link)
                return content_str

            new_link = NEWARA_LINK + "post/" + str(new_article_id)
            return replace_link(content_str.replace(old_link, new_link, 1))

    # case 3: link is query on all boards
    elif len(path) > 2 and path[2] == 'search':
        search_word_pos = path[3].find('search_word=') + 12
        search_word = path[3][search_word_pos:]

        new_link = NEWARA_LINK + 'board?query=' + search_word

        return replace_link(content_str.replace(old_link, new_link, 1))

    # case 4: 전체게시판/스크랩북의 게시물
    elif path[1] == 'all' or path[1] == 'scrapbook':
        if len(path) > 2:
            try:
                old_id = int(path[2].split('#')[0])
                new_article_id = article_id_to_newid_dict.get(old_id, None)

            except (KeyError, ValueError):
                corner_cases.append(old_link)
                return content_str

            new_link = NEWARA_LINK + "post/" + str(new_article_id)

        elif path[1] == 'scrapbook':
            new_link = NEWARA_LINK + 'archive'

        else:
            new_link = NEWARA_LINK + 'board'

        return replace_link(content_str.replace(old_link, new_link, 1))

    # case 5: 메인페이지
    elif path[1] == 'main':
        return replace_link(content_str.replace(old_link, NEWARA_LINK, 1))

    # case 6: link to blacklist page
    elif old_link.find('blacklist') > -1:
        new_link = NEWARA_LINK + 'myinfo' # 뉴아라에서는 blacklist를 마이페이지에서 볼 수 있음
        return replace_link(content_str.replace(old_link, new_link, 1))

    else: # if not in these cases, accumulate link in a list and print later, to find corner cases
        corner_cases.append(old_link)
        return content_str


def update_ara_links():
    # check articles
    FETCH_NUM = 600000
    newara_middle_cursor.execute(query=read_queries['core_article'].format(FETCH_NUM))
    core_articles = newara_middle_cursor.fetchall()

    # create dictionary mapping old article id -> new article id
    for a in core_articles:
        article_id_to_newid_dict[a['id']] = a['new_id']

    newara_middle_cursor.execute(query=read_queries['core_comment'].format(FETCH_NUM))
    core_comment = newara_middle_cursor.fetchall()

    # create dictionary mapping old comment id -> new comment id
    for c in core_comment:
        comment_id_to_newid_dict[c['id']] = c['new_id']
        comment_get_parent_article_id[c['id']] = c['parent_article_id']

    newara_middle_cursor.execute(query=read_queries['core_attachment'].format(FETCH_NUM))
    core_attachment = newara_middle_cursor.fetchall()

    # create dictionary mapping old attachment id -> attachment path
    for att in core_attachment:
        attachment_id_to_path_dict[att['id']] = att['file']

    # identify all articles that contain "ara.kaist.ac.kr"
    newara_consecutive_cursor.execute(query=read_queries['articles_with_ara_links'].format(FETCH_NUM))
    articles_with_links = newara_consecutive_cursor.fetchall()

    relink_articles(articles_with_links)

    # check comments
    print('start relinking comments')

    # identify all comments that contain "ara.kaist.ac.kr"
    newara_consecutive_cursor.execute(query=read_queries['comments_with_ara_links'].format(FETCH_NUM))
    comments_with_links = newara_consecutive_cursor.fetchall()

    relink_comments(comments_with_links)

    print("corner cases: ")
    for c in corner_cases:
        print(c)