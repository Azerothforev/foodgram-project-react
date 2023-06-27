from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def add_del_recipesview(request, model, recipeminifiedserializer, **kwargs):
    """
    Представление для добавления и удаления рецептов.

    Args:
        request (HttpRequest): HTTP-запрос.
        model (Model): Модель для создания/удаления связи с рецептом.
        recipeminifiedserializer (Serializer): Сериализатор для минимальной информации о рецепте.
        **kwargs: Дополнительные аргументы.

    Returns:
        HttpResponse: HTTP-ответ.

    Raises:
        Http404: Если рецепт не найден.
    """
    recipe_id = kwargs['pk']
    user = request.user
    recipe_obj = get_object_or_404(Recipe, pk=recipe_id)
    data = {
        "id": recipe_id,
        "name": recipe_obj.name,
        "image": recipe_obj.image,
        "cooking_time": recipe_obj.cooking_time,
    }

    if request.method == 'POST':
        serializer = recipeminifiedserializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            model.objects.create(user=user, recipe_id=recipe_id)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        get_object_or_404(model, user=user, recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
