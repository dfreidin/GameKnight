from flask import Flask
from flask.logging import default_handler
from gk_graphql.schema import schema
# from gk_graphql.dummy_schema import schema
from flask_graphql import GraphQLView
import logging
from os import getenv

import gk_graphql.db as db
import gk_graphql.aws as aws

db_name = getenv("DB_NAME", "game-knight-dev")
db_secret = aws.get_secret()
db_conn_info = {
    "dbname": db_name,
    "user": db_secret.get("username"),
    "password": db_secret.get("password"),
    "host": db_secret.get("host"),
    "port": int(db_secret.get("port"))
}

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
logging.getLogger().addHandler(default_handler)

pool = db.create_connection_pool(db_config=db_conn_info)

@app.route("/hello")
def hello_route():
    return "Hello, World!"

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,
        root_value={
            "pool": pool,
            "dataloaders": {
                "users": db.create_users_dataloader(pool),
                "games": db.create_games_dataloader(pool),
                "groups": db.create_groups_dataloader(pool),
                "ratings": db.create_ratings_dataloader(pool),
                "members": db.create_members_dataloader(pool),
                "friends": db.create_friends_dataloader(pool)
            }
        }
    )
)