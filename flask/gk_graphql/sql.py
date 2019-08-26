SELECT_USERS_BY_USERNAME = """
    SELECT * FROM users
    WHERE username = ANY(%(users)s);
"""

SELECT_USERS_BY_ID = """
    SELECT * FROM users
    WHERE id = ANY(%(ids)s);
"""

SELECT_GROUPS_BY_ID = """
    SELECT * FROM groups
    WHERE id = ANY(%(ids)s);
"""

SELECT_GAMES_BY_ID = """
    SELECT * FROM games
    WHERE id = ANY(%(ids)s);
"""

SELECT_RATINGS_BY_USER_ID = """
    SELECT * FROM ratings
    WHERE user_id = ANY(%(user_ids)s);
"""

SELECT_RATINGS_BY_ID = """
    SELECT * FROM ratings
    WHERE id = ANY(%(ids)s);
"""

SELECT_SPECIFIC_RATINGS_BY_USER_ID = """
    SELECT * FROM ratings
    WHERE user_id = ANY(%(user_ids)s)
    AND game_id = ANY(%(game_ids)s);
"""

SELECT_OWNED_GAMES_BY_USER_ID = """
    SELECT * FROM ratings
    WHERE owned
    AND user_id = ANY(%(user_ids)s);
"""

SELECT_MEMBERS_BY_USER_ID = """
    SELECT * FROM members
    WHERE user_id = ANY(%(user_ids)s);
"""

SELECT_MEMBERS_BY_GROUP_ID = """
    SELECT * FROM members
    WHERE group_id = ANY(%(group_ids)s);
"""

SELECT_MEMBERS_BY_ID = """
    SELECT * FROM members
    WHERE id = ANY(%(ids)s);
"""

SELECT_ADMINS_BY_USER_ID = """
    SELECT * FROM members
    WHERE is_admin
    AND user_id = ANY(%(user_ids)s);
"""

SELECT_ADMINS_BY_GROUP_ID = """
    SELECT * FROM members
    WHERE is_admin
    AND group_id = ANY(%(group_ids)s);
"""

SELECT_FRIENDS_INSTIGATED = """
    SELECT * FROM friends
    WHERE friends.instigator_id = ANY(%(user_ids)s);
"""

SELECT_FRIENDS_REQUESTED = """
    SELECT * FROM friends
    WHERE friends.requested_id = ANY(%(user_ids)s);
"""

SELECT_ACCEPTED_FRIENDS_INSTIGATED = """
    SELECT users.* FROM friends
    JOIN users ON friends.requested_id = users.id
    WHERE accepted
    AND friends.instigator_id = ANY(%(user_ids)s);
"""

SELECT_ACCEPTED_FRIENDS_REQUESTED = """
    SELECT users.* FROM friends
    JOIN users ON friends.instigator_id = users.id
    WHERE accepted
    AND friends.requested_id = ANY(%(user_ids)s);
"""

SELECT_FRIENDS_BY_ID = """
    SELECT * FROM friends
    WHERE id = ANY(%(ids)s);
"""

INSERT_USER = """
    INSERT INTO users (
        username
    ) VALUES (
        %(username)s
    ) RETURNING id;
"""

INSERT_GAME = """
    INSERT INTO games (
        name,
        bgg_id
    ) VALUES (
        %(name)s,
        %(bgg_id)s
    ) RETURNING id;
"""

INSERT_GROUP = """
    INSERT INTO groups (
        name
    ) VALUES (
        %(name)s
    ) RETURNING id;
"""

INSERT_MEMBER = """
    INSERT INTO members (
        user_id,
        group_id,
        is_admin
    ) VALUES (
        (SELECT id FROM users WHERE username = %(username)s),
        (SELECT id FROM groups WHERE name = %(group_name)s),
        %(is_admin)s
    ) RETURNING id;
"""

INSERT_RATING = """
    INSERT INTO ratings (
        user_id,
        game_id,
        rating,
        owned
    ) VALUES (
        (SELECT id FROM users WHERE username = %(username)s),
        (SELECT id FROM games WHERE name = %(game_name)s),
        %(rating)s,
        %(owned)s
    ) RETURNING id;
"""

INSERT_FRIEND = """
    INSERT INTO friends (
        instigator_id,
        requested_id,
        accepted
    ) VALUES (
        %(instigator_id)s,
        %(requested_id)s,
        %(accepted)s
    ) RETURNING id;
"""

UPDATE_GROUP = """
    UPDATE groups
    SET name = %(name)s
    WHERE id = %(id)s
    RETURNING id;
"""

UPDATE_MEMBER = """
    UPDATE members
    SET is_admin = %(is_admin)s
    WHERE user_id = (SELECT id FROM users WHERE username = %(username)s)
    AND group_id = (SELECT id FROM groups WHERE name = %(group_name)s)
    RETURNING id;
"""

UPDATE_RATING = """
    UPDATE ratings
    SET rating = %(rating)s,
        owned = %(owned)s
    WHERE user_id = (SELECT id FROM users WHERE username = %(username)s)
    AND game_id = (SELECT id FROM games WHERE name = %(game_name)s)
    RETURNING id;
"""

UPDATE_FRIEND = """
    UPDATE friends
    SET accepted = %(accepted)s
    WHERE instigator_id = %(instigator_id)s
    AND requested_id = %(requested_id)s
    RETURNING id;
"""

DELETE_USER = """
    DELETE FROM users
    WHERE user_id = %(user_id)s
    RETURNING id;
"""

DELETE_GROUP = """
    DELETE FROM groups
    WHERE id = %(id)s
    RETURNING id;
"""

DELETE_MEMBER = """
    DELETE FROM members
    WHERE user_id = %(user_id)s
    AND group_id = %(group_id)s
    RETURNING id;
"""

DELETE_RATING = """
    DELETE FROM ratings
    WHERE user_id = %(user_id)s
    AND game_id = %(game_id)s
    RETURNING id;
"""

DELETE_FRIEND = """
    DELETE FROM friends
    WHERE instigator_id = %(instigator_id)s
    AND requested_id = %(requested_id)s
    RETURNING id;
"""