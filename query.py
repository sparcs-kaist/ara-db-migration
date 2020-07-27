read_queries = {
    # 'articles': """select A.id, A.title, A.board_id, content, A.author_id, B.nickname, A.date,
    #                A.hit, A.positive_vote, A.negative_vote, A.deleted, A.destroyed, A.last_reply_date
    #                from articles A inner join users B where A.author_id = B.id;""",
    'articles': """select id, title, board_id, content, author_id, date,
                   hit, positive_vote, negative_vote, deleted, destroyed, last_reply_date,
                   root_id, parent_id
                   from articles LIMIT {};""",
    'core_article': """select id, created_at, updated_at, deleted_at, title, content, content_text,
                       is_anonymous, is_content_sexual, is_content_social, hit_count,
                       positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id
                        from core_article LIMIT {};""",
    'core_comment': """select id, created_at, updated_at, deleted_at, content,
                       is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                       created_by_id, parent_article_id, parent_comment_id
                        from core_comment LIMIT {};""",
    'files': """select id, filename, saved_filename, filepath,
                user_id, board_id, article_id, deleted 
                from files LIMIT {};""",

}

write_queries = {
    'core_article': """insert into core_article(id, created_at, updated_at, deleted_at, title, content, content_text,
                       is_anonymous, is_content_sexual, is_content_social, hit_count,
                       positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id)
                       values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_comment': """insert into core_comment(id, created_at, updated_at, deleted_at, content,
                        is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                        created_by_id, parent_article_id, parent_comment_id)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_attachment': """insert into core_attachment(id, created_at, updated_at, deleted_at, file, mime_type, size)
                        values (%s, %s, %s, %s, %s, %s, %s),
}
