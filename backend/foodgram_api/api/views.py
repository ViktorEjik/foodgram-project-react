import csv

from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import FavoriteList, Follow, Ingredient, Recipe, Tag, User

from .filters import RecipeFilter
from .permissions import AdminModeratorAuthorPermission
from .serializers import (CustomUserSerializer, FollowReadSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          TagSerializer)


class CustomUserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
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

    @transaction.atomic
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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    http_method_names = ['get', ]
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    http_method_names = ['get', ]
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
    filter_backends = (SearchFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminModeratorAuthorPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @transaction.atomic
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

    @transaction.atomic
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

    @transaction.atomic
    def add_shopping_list(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if user.shopping_list.filter(recipe=recipe).exists():
            return Response(
                {'message': 'Нельзя добавлять рецепт в лист покупок дважды!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.shopping_list.create(user=user, recipe=recipe)
        return Response(RecipeSerializer(recipe).data)

    @transaction.atomic
    def delete_shopping_list(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_recipe_list = user.shopping_list.filter(recipe=recipe)
        if not shopping_recipe_list.exists():
            return Response({
                'message':
                    'Нельзя удалить рецепт из листа покупок, т.к. его там нет!'
            },
                status=status.HTTP_400_BAD_REQUEST
            )
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
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition":
                    'attachment; filename="somefilename.csv"'
            },
        )
        writer = csv.writer(response)
        shop_cart = (
            request.user.shopping_list.
            values_list(
                'recipe__ingredients__ingredient__name',
                'recipe__ingredients__ingredient__measurement_unit'
            ).annotate(amount=Sum('recipe__ingredients__amount'))
        )

        writer.writerows(shop_cart)

        return response

    @action(methods=['POST', 'DELETE'], detail=True, url_path='shopping_cart')
    def shopping_list(self, request, pk=None):
        if request.method == 'POST':
            return self.add_shopping_list(request, pk)
        return self.delete_shopping_list(request, pk)

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )


@api_view(['GET',], )
def subscriptions(request):
    user = request.user
    if not user.is_authenticated:
        return Response({
            "detail": "Учетные данные не были предоставлены."
        }, status=status.HTTP_401_UNAUTHORIZED)

    following = User.objects.filter(following__user=user)

    recipes_limit = request.query_params.get('recipes_limit', 10)
    return Response(FollowReadSerializer(
        following,
        context={
            'request': request,
            'recipes_limit': recipes_limit
        }, many=True
    ).data, status=status.HTTP_200_OK)
