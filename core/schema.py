import graphene
import graphql_jwt

from users.schema import UserType 
from users.mutations import AuthMutation 

class Query(graphene.ObjectType):
    
    me = graphene.Field(UserType)

    @graphql_jwt.decorators.login_required
    def resolve_me(self, info):
        return info.context.user

    # Add other queries here...
    node = graphene.relay.Node.Field() # If using Relay


class Mutation(AuthMutation, graphene.ObjectType): # Inherit from AuthMutation
    # Mutations from django-graphql-jwt
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field() # Optional: If using refresh token blacklist



schema = graphene.Schema(query=Query, mutation=Mutation)