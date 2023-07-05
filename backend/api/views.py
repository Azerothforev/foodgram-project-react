from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from recipes.models import (
    ShopingCart, FavoriteRecipe, Follow,
    Ingredient, Recipe, Tag, IngredientInRecipe)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CustomUserSerializer, FollowSerializer, IngredientSerializer,
    RecipeAddSerializer, RecipeMinifiedSerializer,
    RecipeSerializer, TagSerializer)
from .utils import add_del_recipesview
from .filters import IngredientsFilter, RecipesFilter

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    """Вьюсет для обработки всех запросов от пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
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
        Возвращает пользователей,
        на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        """
        subscriptions_data = User.objects.filter(
            followers__user=request.user)

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
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientsFilter
    permission_classes = (IsAdminOrReadOnly,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра и редактирования рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    filterset_class = RecipesFilter

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
        url_path='shopping_cart'
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
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Формат TXT."""
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shoppingcart_recipe__user=request.user,
        ).order_by('ingredient__name').values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = f'Список покупок {request.user}:\n'
        for iter, (name, unit, amount) in enumerate(shopping_cart, start=1):
            shopping_list += f'\n {iter}. {name} ({unit}) - {amount}'

        filename = 'data.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
