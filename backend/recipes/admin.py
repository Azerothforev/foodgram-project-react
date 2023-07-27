from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import (
    Tag, Ingredient, Recipe, FavoriteRecipe,
    Follow, ShopingCart, IngredientInRecipe
)

from import_export import resources
from import_export.admin import ImportExportModelAdmin


class IngredientResource(resources.ModelResource):

    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResource]


class IngredientInRecipeInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if not any(form.cleaned_data for form in self.forms):
            raise forms.ValidationError(
                'Необходимо добавить хотя бы один ингредиент.')


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    formset = IngredientInRecipeInlineFormSet


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ['tags']

    def response_add(self, request, obj, post_url_continue=None):
        if not obj.ingredients.exists():
            self.message_user(
                request,
                "Необходимо добавить хотя бы один ингредиент.",
                level='ERROR')
            return HttpResponseRedirect(request.path)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if not obj.ingredients.exists():
            self.message_user(
                request,
                "Необходимо добавить хотя бы один ингредиент.",
                level='ERROR')
            return HttpResponseRedirect(request.path)
        return super().response_change(request, obj)

    def clean(self):
        # Проверка наличия хотя бы одного ингредиента перед сохранением рецепта
        ingredients = self.cleaned_data.get('ingredients')
        if not ingredients.exists():
            raise forms.ValidationError(
                'Необходимо добавить хотя бы один ингредиент.')

        return super().clean()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(Follow)
admin.site.register(ShopingCart)
admin.site.register(IngredientInRecipe)
admin.site.register(Ingredient, IngredientAdmin)
