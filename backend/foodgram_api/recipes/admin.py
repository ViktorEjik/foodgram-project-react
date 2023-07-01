from django.contrib import admin

from .models import (Favorite, Follow, Ingredient, Recipe, ShoppingCart, Tag,
                     User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name', 'date_joined',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time',
                    'text', 'pub_date', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
