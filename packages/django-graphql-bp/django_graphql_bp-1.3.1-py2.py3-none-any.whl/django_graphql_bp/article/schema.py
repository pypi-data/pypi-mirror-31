import graphene
from django import forms
from django_graphql_bp.graphql.operations import connections, fields, interfaces, mutations
from django_graphql_bp.article.forms import ArticleForm, ArticleImageForm
from django_graphql_bp.article.models import Article, ArticleImage
from graphene_django import DjangoObjectType
from graphql.execution.base import ResolveInfo


class ArticleNode(DjangoObjectType):
    class Meta:
        connection_class = connections.CountableConnection
        filter_fields = ['is_active', 'slug']
        interfaces = (graphene.relay.Node, interfaces.DjangoPkInterface)
        model = Article


class ArticleImageNode(DjangoObjectType):
    class Meta:
        filter_fields = ['id']
        interfaces = (graphene.relay.Node, interfaces.DjangoPkInterface)
        model = ArticleImage


class ArticleInput:
    content = graphene.String()
    is_active = graphene.Boolean()
    subtitle = graphene.String()
    title = graphene.String()


class ArticleImageInput:
    article = graphene.Int()
    is_featured = graphene.Boolean()


class CreateArticle(mutations.MutationAccess, mutations.MutationCreate, graphene.relay.ClientIDMutation):
    form = ArticleForm
    node = graphene.Field(ArticleNode)

    class Input(ArticleInput):
        pass

    @classmethod
    def get_form(cls, info: ResolveInfo, input: dict) -> forms.ModelForm:
        input.update({'author': info.context.user.pk})
        return super(CreateArticle, cls).get_form(info, input)


class UpdateArticle(mutations.MutationAccess, mutations.MutationUpdate, graphene.relay.ClientIDMutation):
    form = ArticleForm
    is_update = True
    model = Article
    node = graphene.Field(ArticleNode)

    class Input(ArticleInput):
        pk = graphene.Int(required=True)


class DeleteArticle(mutations.MutationAccess, mutations.MutationDelete, graphene.relay.ClientIDMutation):
    is_delete = True
    model = Article
    node = graphene.Field(ArticleNode)

    class Input:
        pk = graphene.Int(required=True)


class CreateArticleImage(mutations.MutationAccess, mutations.MutationCreate, graphene.relay.ClientIDMutation):
    form = ArticleImageForm
    is_create = True
    node = graphene.Field(ArticleImageNode)

    class Input(ArticleImageInput):
        pass


class UpdateArticleImage(mutations.MutationAccess, mutations.MutationUpdate, graphene.relay.ClientIDMutation):
    form = ArticleImageForm
    is_update = True
    model = ArticleImage
    node = graphene.Field(ArticleImageNode)

    class Input(ArticleImageInput):
        pk = graphene.Int(required=True)


class DeleteArticleImage(mutations.MutationAccess, mutations.MutationDelete, graphene.relay.ClientIDMutation):
    is_delete = True
    model = ArticleImage
    node = graphene.Field(ArticleImageNode)

    class Input:
        pk = graphene.Int(required=True)


class Query:
    articles = fields.SearchConnectionField(ArticleNode, pk=graphene.Int(), sort=graphene.Argument(graphene.String))


class Mutation:
    create_article = CreateArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()

    create_article_image = CreateArticleImage.Field()
    update_article_image = UpdateArticleImage.Field()
    delete_article_image = DeleteArticleImage.Field()
