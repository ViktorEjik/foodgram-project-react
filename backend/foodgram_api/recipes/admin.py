from django.contrib import admin

from .models import (FavoriteList, Follow, Ingredient, IngredientAmount,
                     Recipe, RecipeIngredient, RecipeTag, ShoppingList, Tag,
                     User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',
                    'first_name', 'last_name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'colore')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'text',
                    'cooking_time', 'image')


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient',
                    'recipe')


@admin.register(Follow)
class FolloeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


@admin.register(FavoriteList)
class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(ShoppingList)
class ShoppingRecipeListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(IngredientAmount)
class IngredientAmauntAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'amount')
