from django.contrib import admin

from .models import (
    Tag, Ingredient, Recipe, FavoriteRecipe,
    Follow, ShopingCart, IngredientInRecipe
)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(Follow)
admin.site.register(ShopingCart)
admin.site.register(IngredientInRecipe)
