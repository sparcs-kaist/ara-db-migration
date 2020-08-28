from datetime import datetime

from mysql import ara_cursor, newara_middle_cursor, newara_middle_db, newara_consecutive_cursor, newara_consecutive_db
from query import read_queries, write_queries, update_queries


NEWARA_LINK = 'https://newara.dev.sparcs.org/'

corner_cases = []

article_id_to_newid_dict = {}
attachment_id_to_newid_dict = {}
comment_id_to_newid_dict = {}
comment_get_parent_article_id = {}

old_board_name_to_new_name = {
    'notice': 'portal',
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

    for article in articles_with_links:
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

    for c in comments_with_links:
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

    # identify which candidate is end of link
    link_end_pos = min((link_end1, link_end2, link_end3, link_end4, link_end5, link_end6, link_end7))

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

    # case 1: variation of ara's main page (ex. mobile main page)
    if len(path) == 1:
        return content_str

    # case 2: link is board, post, or attachment file
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
            new_attachment_id = attachment_id_to_newid_dict[old_attachment_id]
            # TODO: 현재 프론트의 첨부 파일 링크가 구현되지 않아서 attachment/로 넣었습니다. 추후에 구현되면 수정하겠습니다.
            new_link = NEWARA_LINK + "attachment/" + str(new_attachment_id)
            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-c: write
        elif path[3] == 'write':
            new_link = NEWARA_LINK + 'write'
            return replace_link(content_str.replace(old_link, new_link, 1))

        # case 2-d: link to a post: contains board/{boardName}/{articleID}
        else:
            try:
                old_id = int(path[3].split('#')[0])
                new_article_id = article_id_to_newid_dict.get(old_id, None)
                if new_article_id is None:
                    new_comment_id = comment_id_to_newid_dict[old_id]
                    new_article_id = comment_get_parent_article_id[new_comment_id]

            except KeyError: # unable to index article/comment
                corner_cases.append(old_link)
                return content_str

            except ValueError: # value in link is not a number
                corner_cases.append(old_link)
                return content_str

            new_link = NEWARA_LINK + "post/" + str(new_article_id)
            return replace_link(content_str.replace(old_link, new_link, 1))

    # case 3: 전체게시판/스크랩북의 게시물
    elif path[1] == 'all' or path[1] == 'scrapbook':
        if len(path) > 2:
            try:
                old_id = int(path[2].split('#')[0])
                new_article_id = article_id_to_newid_dict.get(old_id, None)

            except KeyError:
                return content_str

            except ValueError:
                return content_str

            new_link = NEWARA_LINK + "post/" + str(new_article_id)
            return replace_link(content_str.replace(old_link, new_link, 1))

        else:
            new_link = NEWARA_LINK + 'board'
            return replace_link(content_str.replace(old_link, new_link, 1))

    elif path[1] == 'main':
        return replace_link(content_str.replace(old_link, NEWARA_LINK, 1))

    # TODO: 현재 black list page가 없어서 이 부분을 구현하지 못했습니다. 추후에 blacklist가 생기면 구현하겠습니다.
    # case 4: link to blacklist page
    elif old_link.find('blacklist') > -1:
        return content_str

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

    # create dictionary mapping old attachment id -> new attachment id
    for att in core_attachment:
        attachment_id_to_newid_dict[att['id']] = att['new_id']

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