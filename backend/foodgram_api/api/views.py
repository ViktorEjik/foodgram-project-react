from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag, User)

from .filters import RecipeFilter
from .pagination import Pagination
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'DELETE':
            follow = get_object_or_404(Follow, user=user, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        Follow.objects.get_or_create(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        following = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(following)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (SearchFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAdminAuthorOrReadOnly, )
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']}"
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
