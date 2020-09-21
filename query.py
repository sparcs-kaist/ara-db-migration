read_queries = {
    # 'articles': """select A.id, A.title, A.board_id, content, A.author_id, B.nickname, A.date,
    #                A.hit, A.positive_vote, A.negative_vote, A.deleted, A.destroyed, A.last_reply_date
    #                from articles A inner join users B where A.author_id = B.id;""",
    'articles': """select id, title, board_id, content, author_id, date,
                   hit, positive_vote, negative_vote, deleted, destroyed, last_reply_date,
                   root_id, parent_id
                   from articles LIMIT {};""",
    'core_article': """select id, new_id, created_at, updated_at, deleted_at, title, content, content_text,
                       is_anonymous, is_content_sexual, is_content_social, hit_count,
                       positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id,
                       parent_topic_id, url
                        from core_article LIMIT {};""",
    'core_comment': """select id, new_id, created_at, updated_at, deleted_at, content,
                       is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                       created_by_id, parent_article_id, parent_comment_id
                        from core_comment LIMIT {};""",
    'files': """select id, filename, saved_filename, filepath,
                user_id, board_id, article_id, deleted 
                from files LIMIT {};""",
    'users': """select id, username, password, password_reset, nickname, email, signature,
                self_introduction, default_language, campus, activated, widget, layout,
                join_time, last_login_time, last_logout_time, last_login_ip, is_sysop,
                authentication_mode, listing_mode, activated_backup, deleted, genuine_email_address
                from users LIMIT {};""",

    'core_attachment': """select id, new_id, created_at, updated_at, deleted_at, file, mimetype, size
                            from core_attachment LIMIT {};""",
    'core_article_attachments': """select id, article_id, attachment_id
                            from core_article_attachments LIMIT {};""",
    'auth_user': """select id, new_id, password, last_login, is_superuser, username, first_name, last_name,
                    email, is_staff, is_active, date_joined
                    from auth_user LIMIT {};""",
    'user_userprofile': """select created_at, updated_at, deleted_at, uid, sid, sso_user_info,
                            picture, nickname, nickname_updated_at, see_sexual, see_social, extra_preferences,
                            user_id, new_id, is_newara, ara_id, `group`
                            from user_userprofile LIMIT {};""",

    'auth_user_consecutive': """select id, password, last_login, is_superuser, username, first_name, last_name,
                   email, is_staff, is_active, date_joined
                   from auth_user LIMIT {};""",
    'user_userprofile_consecutive': """select created_at, updated_at, deleted_at, uid, sid, sso_user_info,
                           picture, nickname, nickname_updated_at, see_sexual, see_social, extra_preferences,
                           user_id, is_newara, ara_id, `group`
                           from user_userprofile LIMIT {};""",
    'core_article_consecutive': """select id, created_at, updated_at, deleted_at, title, content, content_text,
                    is_anonymous, is_content_sexual, is_content_social, hit_count,
                    positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id,
                    parent_topic_id, url
                     from core_article LIMIT {};""",
    'core_comment_consecutive': """select id, created_at, updated_at, deleted_at, content,
                    is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                    created_by_id, parent_article_id, parent_comment_id
                     from core_comment LIMIT {};""",
    'core_attachment_consecutive': """select id, created_at, updated_at, deleted_at, file, mimetype, size
                           from core_attachment LIMIT {};""",
    'articles_with_ara_links': """select * from core_article where content like '%ara.kaist.ac.kr/%';""",
    'comments_with_ara_links': """select * from core_comment where content like '%ara.kaist.ac.kr/%';""",

}

# queries without 'consecutive' contain the column 'new_id'
# queries with 'consecutive' do not contain the column 'new_id'
write_queries = {
    'core_article': """insert into core_article(id, new_id, created_at, updated_at, deleted_at, title, content, content_text,
                       is_anonymous, is_content_sexual, is_content_social, hit_count,
                       positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id,
                       parent_topic_id, url)
                       values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_comment': """insert into core_comment(id, new_id, created_at, updated_at, deleted_at, content,
                        is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                        created_by_id, parent_article_id, parent_comment_id)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_attachment': """insert into core_attachment(id, new_id, created_at, updated_at, deleted_at, file, mimetype, size)
                        values (%s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_article_attachments': """insert into core_article_attachments(id, article_id, attachment_id)
                                    values (%s, %s, %s)""",
    'auth_user': """insert into auth_user(id, new_id, password, last_login, is_superuser, username,
                    first_name, last_name, email, is_staff, is_active, date_joined)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'user_userprofile': """insert into user_userprofile(created_at, updated_at, deleted_at,
                            uid, sid, sso_user_info, picture, nickname, nickname_updated_at, see_sexual, see_social,
                            extra_preferences, user_id, new_id, is_newara, ara_id, `group`)
                            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",

    'core_article_consecutive': """insert into core_article(id, created_at, updated_at, deleted_at, title, content, content_text,
                    is_anonymous, is_content_sexual, is_content_social, hit_count,
                    positive_vote_count, negative_vote_count, commented_at, created_by_id, parent_board_id,
                    parent_topic_id, url, migrated_hit_count, migrated_positive_vote_count, migrated_negative_vote_count)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_comment_consecutive': """insert into core_comment(id, created_at, updated_at, deleted_at, content,
                     is_anonymous, positive_vote_count, negative_vote_count, attachment_id, 
                     created_by_id, parent_article_id, parent_comment_id)
                     values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'core_attachment_consecutive': """insert into core_attachment(id, created_at, updated_at, deleted_at, file, mimetype, size)
                     values (%s, %s, %s, %s, %s, %s, %s)""",
    'core_article_attachments': """insert into core_article_attachments(id, article_id, attachment_id)
                                 values (%s, %s, %s)""",
    'auth_user_consecutive': """insert into auth_user(id, password, last_login, is_superuser, username,
                 first_name, last_name, email, is_staff, is_active, date_joined)
                 values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    'user_userprofile_consecutive': """insert into user_userprofile(created_at, updated_at, deleted_at,
                         uid, sid, sso_user_info, picture, nickname, nickname_updated_at, see_sexual, see_social,
                         extra_preferences, user_id, is_newara, ara_id, `group`)
                         values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
}

delete_queries = {
    'core_article': """delete from core_article LIMIT {};""",
    'core_comment': """delete from core_comment order by id DESC LIMIT 1;""",
    'core_attachment': """delete from core_attachment LIMIT {};""",
    'core_article_attachments': """delete from core_article_attachments LIMIT {};""",
    'user_userprofile': """delete from user_userprofile LIMIT {};""",
    'auth_user': """delete from auth_user LIMIT {};""",
}

update_queries = {
    'core_article_content': """UPDATE core_article SET content = %s, content_text = %s WHERE id = %s;""",
    'core_comment_content': """UPDATE core_comment SET content = %s WHERE id = %s;""",

}
