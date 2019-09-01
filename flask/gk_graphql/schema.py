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
    rating = graphene.Int()
    owned = graphene.Boolean()

class InputMember(graphene.InputObjectType):
    username = graphene.String(required=True)
    group_name = graphene.String(required=True)
    is_admin = graphene.Boolean()

class CreateUser(graphene.Mutation):
    class Arguments:
        user = InputUser(required=True)
    Output = User
    def mutate(self, info, user):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["users"]
        db_user = {
            "username": user.username
        }
        user_id = db.mutate(pool, sql.INSERT_USER, db_user).get("id")
        return dl.load(user_id).then(lambda u: User(**u))

class CreateGame(graphene.Mutation):
    class Arguments:
        game = InputGame(required=True)
    Output = Game
    def mutate(self, info, game):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["games"]
        db_game = {
            "name": game.name,
            "bgg_id": game.bgg_id
        }
        game_id = db.mutate(pool, sql.INSERT_GAME, db_game).get("id")
        return dl.load(game_id).then(lambda g: Game(**g))

class CreateGroup(graphene.Mutation):
    class Arguments:
        group = InputGroup(required=True)
    Output = Group
    def mutate(self, info, group):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["groups"]
        db_group = {
            "name": group.name
        }
        group_id = db.mutate(pool, sql.INSERT_GROUP, db_group).get("id")
        return dl.load(group_id).then(lambda g: Group(**g))

class CreateRating(graphene.Mutation):
    class Arguments:
        rating = InputRating(required=True)
    Output = Rating
    def mutate(self, info, rating):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["ratings"]
        db_rating = {
            "username": rating.username,
            "game_name": rating.game_name,
            "rating": rating.rating,
            "owned": rating.owned
        }
        rating_id = db.mutate(pool, sql.INSERT_RATING, db_rating).get("id")
        return dl.load(rating_id).then(lambda g: Rating(**g))

class CreateMembership(graphene.Mutation):
    class Arguments:
        membership = InputMember(required=True)
    Output = Membership
    def mutate(self, info, membership):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["memberships"]
        db_membership = {
            "username": membership.username,
            "group_name": membership.group_name,
            "is_admin": membership.is_admin
        }
        membership_id = db.mutate(pool, sql.INSERT_MEMBER, db_membership).get("id")
        return dl.load(membership_id).then(lambda g: Membership(**g))

class UpdateRating(graphene.Mutation):
    class Arguments:
        rating = InputRating(required=True)
    Output = Rating
    def mutate(self, info, rating):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["ratings"]
        db_rating = {
            "username": rating.username,
            "game_name": rating.game_name,
            "rating": rating.rating,
            "owned": rating.owned
        }
        rating_id = db.mutate(pool, sql.UPDATE_RATING, db_rating).get("id")
        return dl.load(rating_id).then(lambda g: Rating(**g))

class UpdateMembership(graphene.Mutation):
    class Arguments:
        membership = InputMember(required=True)
    Output = Membership
    def mutate(self, info, membership):
        pool = info.root_value["pool"]
        dl = info.root_value["dataloaders"]["memberships"]
        db_membership = {
            "username": membership.username,
            "group_name": membership.group_name,
            "is_admin": membership.is_admin
        }
        membership_id = db.mutate(pool, sql.UPDATE_MEMBER, db_membership).get("id")
        return dl.load(membership_id).then(lambda g: Membership(**g))

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_game = CreateGame.Field()
    create_group = CreateGroup.Field()
    create_rating = CreateRating.Field()
    create_membership = CreateMembership.Field()
    update_rating = UpdateRating.Field()
    update_membership = UpdateMembership.Field()

schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)