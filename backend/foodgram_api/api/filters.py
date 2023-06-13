from django_filters import rest_framework as filters

from recipes.models import FavoriteList, Recipe, ShoppingRecipeList, Tag, User


class RecipeFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    author = filters.ModelMultipleChoiceFilter(
        to_field_name='id',
        queryset=User.objects.all()
    )

    is_favorite = filters.BooleanFilter(
        method='get_is_favorite'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorite', 'is_in_shopping_cart')

    def get_is_favorite(self, queryset, name, value):
        user = self.request.user
        if not (user.is_authenticated and value):
            return queryset

        favorite_list = FavoriteList.objects.filter(user=user)
        return Recipe.objects.filter(
            id__in=favorite_list.values_list('recipe'))

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not (user.is_authenticated and value):
            return queryset
        shopping_list = ShoppingRecipeList.objects.filter(user=user)
        return Recipe.objects.filter(
            id__in=shopping_list.values_list('recipe'))
