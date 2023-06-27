from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUsersViewSet, TagsViewSet,
                    IngredientsViewSet, RecipesViewSet)

router = DefaultRouter()
router.register('users', CustomUsersViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')

recipes_extra_patterns = [
    path(
        'download_shopping_cart/',
        RecipesViewSet.as_view({'get': 'download_shopping_cart'}),
        name='recipe-download-shopping-cart'
    ),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/', include(recipes_extra_patterns)),
]
