from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, User


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

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not (user.is_authenticated and value):
            return queryset

        favorite_list = Recipe.objects.filter(favoritelist__user=user)
        return favorite_list

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not (user.is_authenticated and value):
            return queryset
        shopping_list = Recipe.objects.filter(shopping_list__user=user)
        return shopping_list
