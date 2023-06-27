from django.contrib import admin
from .models import Tag, Ingredient, Recipe, FavoriteRecipe, Follow, Cart, IngredientInRecipe


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(Follow)
admin.site.register(Cart)
admin.site.register(IngredientInRecipe)
