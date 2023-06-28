from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    ShopingCart, FavoriteRecipe, Follow, Ingredient, Recipe, Tag)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CustomUserSerializer, FollowSerializer, IngredientSerializer,
    RecipeAddSerializer, RecipeMinifiedSerializer,
    RecipeSerializer, TagSerializer)
from .utils import add_del_recipesview

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    """Вьюсет для обработки всех запросов от пользователей."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    authentication_classes = (TokenAuthentication,)
    pagination_class = PageNumberPagination

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        """Подписаться на пользователя."""
        user = request.user
        author_id = kwargs['id']
        author_obj = get_object_or_404(User, id=author_id)

        serializer = FollowSerializer(
            instance=author_obj,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            Follow.objects.create(
                user=user, author_id=author_id
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        """Отписаться от пользователя."""
        user = request.user
        author_id = kwargs['id']

        if get_object_or_404(
            Follow,
            user=user,
            author_id=author_id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """
        Возвращает авторов, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        """
        subscriptions_data = User.objects.filter(followers__user=request.user)

        page = self.paginate_queryset(subscriptions_data)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)

    def get_serializer_class(self):
        """
        Возвращает нужный сериализатор при разных операциях:
        GET, DELETE - RecipeSerializer;
        POST, UPDATE, DELETE - RecipeAddSerializer.
        """
        if self.action in ('create', 'partial_update'):
            return RecipeAddSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def cart(self, request, **kwargs):
        """Добавить или удалить рецепт из списка покупок."""
        return add_del_recipesview(
            request, ShopingCart, RecipeMinifiedSerializer, **kwargs
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        """Добавить или удалить рецепт в избранных у пользователя."""
        return add_del_recipesview(
            request, FavoriteRecipe, RecipeMinifiedSerializer, **kwargs
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """
        Скачать список покупок в формате TXT.
        Доступно только авторизованным пользователям.
        """
        user = request.user

        shopping_cart = ShopingCart.objects.filter(user=user)

        content = "Shopping Cart:\n"
        for item in shopping_cart:
            content += (
                f"- {item.ingredient.name}: {item.quantity} {item.unit}\n")

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"')

        return response
