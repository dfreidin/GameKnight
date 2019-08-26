from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from promise import Promise
from promise.dataloader import DataLoader
import json
import logging

import gk_graphql.sql as sql

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_db_connection_info():
    with open("gk_graphql/db_config.json") as f:
        db_config = json.load(f)
    return db_config

def create_connection_pool():
    db_config = load_db_connection_info()
    pool = ThreadedConnectionPool(1, 10, **db_config)
    return pool

@contextmanager
def get_connection(pool):
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

def fetch(pool, query, subs):
    with get_connection(pool) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, subs)
            try:
                results = cursor.fetchall()
            except:
                results = None
    return [dict(r) for r in results]

def mutate(pool, query, subs):
    with get_connection(pool) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, subs)
            try:
                results = cursor.fetchone()
            except:
                results = None
    return results

def create_users_dataloader(pool):
    class UserLoader(DataLoader):
        def batch_load_fn(self, keys):
            users = fetch(pool, sql.SELECT_USERS_BY_ID, {"ids": keys})
            users_dict = {u["id"]: u for u in users if u}
            return Promise.resolve([users_dict[k] for k in keys])
    return UserLoader()

def create_games_dataloader(pool):
    class GameLoader(DataLoader):
        def batch_load_fn(self, keys):
            games = fetch(pool, sql.SELECT_GAMES_BY_ID, {"ids": keys})
            games_dict = {g["id"]: g for g in games if g}
            return Promise.resolve([games_dict[k] for k in keys])
    return GameLoader()

def create_groups_dataloader(pool):
    class GroupLoader(DataLoader):
        def batch_load_fn(self, keys):
            groups = fetch(pool, sql.SELECT_GROUPS_BY_ID, {"ids": keys})
            groups_dict = {g["id"]: g for g in groups if g}
            return Promise.resolve([groups_dict[k] for k in keys])
    return GroupLoader()

def create_ratings_dataloader(pool):
    class UserLoader(DataLoader):
        def batch_load_fn(self, keys):
            ratings = fetch(pool, sql.SELECT_RATINGS_BY_ID, {"ids": keys})
            ratings_dict = {r["id"]: r for r in ratings if r}
            return Promise.resolve([ratings_dict[k] for k in keys])
    return UserLoader()

def create_members_dataloader(pool):
    class UserLoader(DataLoader):
        def batch_load_fn(self, keys):
            members = fetch(pool, sql.SELECT_MEMBERS_BY_ID, {"ids": keys})
            members_dict = {m["id"]: m for m in members if m}
            return Promise.resolve([members_dict[k] for k in keys])
    return UserLoader()

def create_friends_dataloader(pool):
    class UserLoader(DataLoader):
        def batch_load_fn(self, keys):
            friends = fetch(pool, sql.SELECT_FRIENDS_BY_ID, {"ids": keys})
            friends_dict = {u["id"]: u for u in friends if u}
            return Promise.resolve([friends_dict[k] for k in keys])
    return UserLoader()