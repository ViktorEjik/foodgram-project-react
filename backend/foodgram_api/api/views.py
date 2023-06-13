import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (FavoriteList, Follow, Ingredient, IngredientAmaunt,
                            Recipe, ShoppingIngredientList, Tag, User)

from .permissions import AdminModeratorAuthorPermission
from .serializers import (CustomUserSerializer, FollowReadSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          TagSerializer)
from .filters import RecipeFilter


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    # http_method_names = ['get', 'post', 'delete']

    def following(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        recipes_limit = request.query_params.get('recipes_limit', 10)
        if user == following:
            return Response(
                {'message': 'Нельзя подписываться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            Follow.objects.create(user=user, author=following)
        except Exception:
            return Response(
                {'message': 'Нельзя подписываться на пользвателя дважды!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            FollowReadSerializer(following, context={
                'request': request,
                'recipes_limit': recipes_limit
            }).data,
            status=status.HTTP_200_OK,
        )

    def unfollow(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        follow = Follow.objects.filter(user=user, author=following)
        if not follow.exists():
            return Response(
                {
                    'message':
                        ('Нельзя отрисаться от пользователя,'
                         ' на которого не подписан!')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='subscribe')
    def follow(self, request, pk=None):
        if request.method == 'POST':
            return self.following(request, pk)
        return self.unfollow(request, pk)

    @action(methods=['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request):
        print('ty')
        user = request.user
        following = user.following.all()
        recipes_limit = request.query_params.get('recipes_limit', 10)
        return Response(FollowReadSerializer(
            following,
            context={
                'request': request,
                'recipes_limit': recipes_limit
            },
            many=True
        ).data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ['get', ]
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    http_method_names = ['get', ]
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminModeratorAuthorPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('tags__recipe_tag__tag',)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def delet_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteList.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {
                'message': 'Нельзя удалить из избранного то чего нет!'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def create_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteList.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            return Response(
                {
                    'message': 'Нельзя добавлять в издранное рецепт дажды!'
                },
                status=status.HTTP_400_BAD_REQUEST)

        favorite = FavoriteList.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(favorite.recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def add_shopping_list(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if user.shopping_recipe_list.filter(recipe=recipe).exists():
            return Response(
                {'message': 'Нельзя добавлять рецепт в лист покупок дважды!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.shopping_recipe_list.create(user=user, recipe=recipe)

        ingredients = recipe.ingredients.all()
        shoping_ingredient_list = user.shoping_ingredient_list.all()

        for ingredient in ingredients:
            if shoping_ingredient_list.filter(
                ingredient=ingredient.ingredient
            ).exists():

                elem = shoping_ingredient_list.get(
                    ingredient=ingredient.ingredient)

                elem.amount += ingredient.amount
                elem.save()
            else:
                ShoppingIngredientList.objects.create(
                    user=user,
                    ingredient=ingredient.ingredient,
                    amount=ingredient.amount
                )
        return Response(RecipeSerializer(recipe).data)

    def delete_shopping_list(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_recipe_list = user.shopping_recipe_list.filter(recipe=recipe)
        if not shopping_recipe_list.exists():
            return Response({
                'message':
                    'Нельзя удалить рецепт из листа покупок, т.к. его там нет!'
            },
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = recipe.ingredients.all()
        shoping_ingredient_list = user.shoping_ingredient_list.all()
        for ingredient in ingredients:
            elem = shoping_ingredient_list.get(
                ingredient=ingredient.ingredient)
            elem.amount -= ingredient.amount
            elem.save()
            if (elem.amount == 0):
                elem.delete()
        shopping_recipe_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite')
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.create_favorite(request, pk)
        return self.delet_favorite(request, pk)

    @action(methods=['GET'],
            permission_classes=(IsAuthenticated,), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition":
                    'attachment; filename="somefilename.csv"'
            },
        )
        writer = csv.writer(response)

        shoping_ingredient_list = user.shoping_ingredient_list.all()

        for ingredient in shoping_ingredient_list:
            writer.writerow([
                ingredient.ingredient.name,
                ingredient.amount,
                ingredient.ingredient.measurement_unit
            ])

        return response

    @action(methods=['POST', 'DELETE'], detail=True, url_path='shopping_cart')
    def shopping_list(self, request, pk=None):
        if request.method == 'POST':
            return self.add_shopping_list(request, pk)
        else:
            return self.delete_shopping_list(request, pk)

    def perform_create(self, serializer):
        tags = serializer.initial_data.get('tags')
        taglist = list()
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag)
            taglist.append(current_tag)

        ingredients = serializer.initial_data.pop('ingredients')
        ingredientslist = list()
        for tupl in ingredients:
            ingredient_id = tupl.get('id')
            amount = tupl.get('amount')
            current_ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient_id
            )

            ingredient_amaunt = IngredientAmaunt.objects.create(
                ingredient=current_ingredient,
                amount=amount,
            )
            ingredientslist.append(ingredient_amaunt)
        serializer.save(
            author=self.request.user, tags=taglist,
            ingredients=ingredientslist
        )

    def perform_update(self, serializer):
        self.perform_create(serializer)
