from flask import Flask
from flask.logging import default_handler
from gk_graphql.schema import schema
# from gk_graphql.dummy_schema import schema
from flask_graphql import GraphQLView
import sys
import logging

import gk_graphql.db as db

app = Flask(__name__)

# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
logging.getLogger().addHandler(default_handler)

pool = db.create_connection_pool()

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