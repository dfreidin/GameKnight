import graphene
import gk_graphql.db as db
import gk_graphql.sql as sql
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Game(graphene.ObjectType):
    id = graphene.Int(required=True)
    name = graphene.String(required=True)
    bgg_id = graphene.Int(required=True)

class Rating(graphene.ObjectType):
    id = graphene.Int(required=True)
    rating = graphene.Int()
    owned = graphene.Boolean(required=True)
    user_id = graphene.Int(required=True)
    game_id = graphene.Int(required=True)
    user = graphene.Field(
        lambda: User,
        required=True
    )
    game = graphene.Field(
        lambda: Game,
        required=True
    )

    def resolve_game(self, info):
        dl = info.root_value["dataloaders"]["games"]
        return dl.load(self.game_id).then(lambda x: Game(**x))

    def resolve_user(self, info):
        dl = info.root_value["dataloaders"]["users"]
        return dl.load(self.user_id).then(lambda x: User(**x))

class User(graphene.ObjectType):
    id = graphene.Int(required=True)
    username = graphene.String(required=True)
    ratings = graphene.List(
        Rating,
        required=True,
        owned=graphene.Boolean(),
        game_ids=graphene.List(graphene.Int)
    )
    friends = graphene.List(
        lambda: User,
        required=True
    )
    memberships = graphene.List(
        lambda: Membership,
        required=True,
        admin=graphene.Boolean()
    )

    def resolve_ratings(self, info, owned=False, game_ids=[]):
        pool = info.root_value["pool"]
        subs = {"user_ids": [self.id]}
        if owned:
            ratings = db.fetch(pool, sql.SELECT_OWNED_GAMES_BY_USER_ID, subs)
        else:
            if game_ids:
                subs.update({"game_ids": game_ids})
                ratings = db.fetch(pool, sql.SELECT_SPECIFIC_RATINGS_BY_USER_ID, subs)
            else:
                ratings = db.fetch(pool, sql.SELECT_RATINGS_BY_USER_ID, subs)
        return [Rating(**r) for r in ratings if r]

    def resolve_friends(self, info):
        pool = info.root_value["pool"]
        subs = {"user_ids": [self.id]}
        friends = db.fetch(pool, sql.SELECT_ACCEPTED_FRIENDS_INSTIGATED, subs)
        friends += db.fetch(pool, sql.SELECT_ACCEPTED_FRIENDS_REQUESTED, subs)
        return [User(**u) for u in friends if u]

    def resolve_memberships(self, info, admin=False):
        pool = info.root_value["pool"]
        subs = {"user_ids": [self.id]}
        if admin:
            memberships = db.fetch(pool, sql.SELECT_ADMINS_BY_USER_ID, subs)
        else:
            memberships = db.fetch(pool, sql.SELECT_MEMBERS_BY_USER_ID, subs)
        return [Membership(**m) for m in memberships if m]

class Friend(graphene.ObjectType):
    id = graphene.Int(required=True)
    accepted = graphene.Boolean(required=True)

class Membership(graphene.ObjectType):
    id = graphene.Int(required=True)
    is_admin = graphene.Boolean(required=True)
    user_id = graphene.Int(required=True)
    group_id = graphene.Int(required=True)
    user = graphene.Field(
        lambda: User,
        required=True
    )
    group = graphene.Field(
        lambda: Group,
        required=True
    )

    def resolve_user(self, info):
        dl = info.root_value["dataloaders"]["users"]
        return dl.load(self.user_id).then(lambda x: User(**x))
    
    def resolve_group(self, info):
        dl = info.root_value["dataloaders"]["groups"]
        return dl.load(self.group_id).then(lambda x: Group(**x))

class Group(graphene.ObjectType):
    id = graphene.Int(required=True)
    name = graphene.String(required=True)
    members = graphene.List(
        Membership,
        required=True,
        admin=graphene.Boolean()
    )

    def resolve_members(self, info, admin=False):
        pool = info.root_value["pool"]
        subs = {"group_ids": [self.id]}
        if(admin):
            memberships = db.fetch(pool, sql.SELECT_ADMINS_BY_GROUP_ID, subs)
        else:
            memberships = db.fetch(pool, sql.SELECT_MEMBERS_BY_GROUP_ID, subs)
        return [Membership(**m) for m in memberships if m]

class Query(graphene.ObjectType):
    users = graphene.List(
        User,
        username=graphene.String()
    )

    def resolve_users(self, info, username):
        users = db.fetch(info.root_value["pool"], sql.SELECT_USERS_BY_USERNAME, {"users": [username]})
        return [User(**u) for u in users if u]

class InputUser(graphene.InputObjectType):
    username = graphene.String(required=True)

class InputGame(graphene.InputObjectType):
    name = graphene.String(required=True)
    bgg_id = graphene.Int(required=True)

class InputGroup(graphene.InputObjectType):
    name = graphene.String(required=True)

class InputRating(graphene.InputObjectType):
    username = graphene.String(required=True)
    game_name = graphene.String(required=True)

class InputMember(graphene.InputObjectType):
    username = graphene.String(required=True)
    group_name = graphene.String(required=True)

class createUser(graphene.Mutation):
    class Arguments:
        user = InputUser(required=True)
    Output = User
    def mutate(self, info, user):
        pool = info.root_value["pool"]
        dl = info.root_value["users"]
        db_user = {
            "username": user.username
        }
        user_id = db.mutate(pool, sql.INSERT_USER, db_user)
        return dl.load(user_id).then(lambda u: User(**u))

schema = graphene.Schema(
    query=Query
)