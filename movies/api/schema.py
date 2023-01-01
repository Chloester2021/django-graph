from graphene import *
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import Movie, Director
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
# this is types.py too, you must convert models to schema in order to query.


class MovieType(DjangoObjectType):
    class Meta:
        model = Movie
    movie_age = String()

    def resolve_movie_age(self, info):
        return 'old' if self.year < 2000 else 'new'


class DirectorType(DjangoObjectType):
    class Meta:
        model = Director


# Relay examples:

class MovieNode(DjangoObjectType):
    class Meta:
        model = Movie
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'year': ['exact',]
        }
        interfaces = (relay.Node,)


class Query(ObjectType):
    # all_movies = List(MovieType)
    # movie = Field(MovieType, id=Int(), title=String())☺
    all_movies = DjangoFilterConnectionField(MovieNode)
    movie = relay.Node.Field(MovieNode)
    all_directors = List(DirectorType)

    def resolve_all_directors(self, info, **kwargs):
        return Director.objects.all()

    # @login_required
    # def resolve_all_movies(self, info, **kwargs):
        return Movie.objects.all()

    # def resolve_movie(self, info, **kwargs):
    #     id = kwargs.get('id')
    #     title = kwargs.get('title')
    #     if id:
    #         return Movie.objects.get(pk=id)
    #     if title:
    #         return Movie.objects.get(title=title)
    #     else:
    #         return []


class MovieCreateMutation(Mutation):
    class Arguments:
        title = String(required=True)
        year = Int(required=True)
    movie = Field(MovieType)

    def mutate(self, info, title, year):
        movie = Movie.objects.create(title=title, year=year)
        return MovieCreateMutation(movie=movie)


class MovieUpdateMutation(Mutation):
    class Arguments:
        title = String(required=False, default_value=None)
        year = Int()
        id = ID(required=True)
    movie = Field(MovieType)

    def mutate(self, info, id, title, year):
        movie = Movie.objects.get(pk=id)

        if title:
            movie.title = title
        if year:
            movie.year = year
        movie.save()
        return MovieUpdateMutation(movie=movie)


class MovieDeleteMutation(Mutation):
    class Arguments:
        id = ID(required=True)
    movie = Field(MovieType)

    def mutate(self, info, id):
        movie = Movie.objects.get(pk=id)
        movie.delete()
        return MovieDeleteMutation(movie=None)


class MovieUpdateMutationRelay(relay.ClientIDMutation):
    class Input:
        title = String()
        id = ID(required=True)
    movie = Field(MovieType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, title, id):
        movie = Movie.objects.get(pk=from_global_id(id)[1])
        if title:
            movie.title = title
        movie.save()
        return MovieUpdateMutationRelay(movie=movie)

# this can be in the __init__.py if there're more than one mutation files.


class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_movie = MovieCreateMutation.Field()
    update_movie = MovieUpdateMutation.Field()
    update_movie_relay = MovieUpdateMutationRelay.Field()
    delete_movie = MovieDeleteMutation.Field()
