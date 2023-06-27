import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import (FavoriteList, Ingredient, IngredientAmount, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingList, Tag,
                            User)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'colore')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'id']


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'id',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        return obj.following.filter(
            user=self.context.get('request').user).exists()


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientAmount
        fields = ('ingredient', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
    is_in_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients',
                  'name', 'author', 'text',
                  'cooking_time', 'image',
                  'is_in_favorited', 'is_in_shopping_cart']

    def get_is_in_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return FavoriteList.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return ShoppingList.objects.filter(
            user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    author = UserSerializer(read_only=True)

    ingredients = IngredientAmountSerializer(many=True, read_only=True)

    image = Base64ImageField()

    is_in_favorited = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients',
                  'name', 'author', 'text',
                  'cooking_time', 'image',
                  'is_in_favorited', 'is_in_shopping_cart']

    def get_ingredients_tags(self):
        tags = self.initial_data.get('tags')
        taglist = list()
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag)
            taglist.append(current_tag)

        ingredients = self.initial_data.get('ingredients')
        ingredientslist = list()
        for tupl in ingredients:
            ingredient_id = tupl.get('id')
            amount = tupl.get('amount')
            current_ingredient = get_object_or_404(
                Ingredient,
                pk=ingredient_id
            )

            ingredient_amaunt = IngredientAmount.objects.create(
                ingredient=current_ingredient,
                amount=amount,
            )
            ingredientslist.append(ingredient_amaunt)
        return taglist, ingredientslist

    @transaction.atomic
    def create(self, validated_data):

        taglist, ingredientslist = self.get_ingredients_tags()

        recipe = Recipe.objects.create(**validated_data)

        recipe_tags = list()
        for tag in taglist:
            recipe_tags.append(RecipeTag(recipe=recipe, tag=tag))

        RecipeTag.objects.bulk_create(recipe_tags)

        recipe_ingredients = list()
        for ingredient in ingredientslist:
            recipe_ingredients.append(RecipeIngredient(
                ingredient=ingredient, recipe=recipe))

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        taglist, ingredientslist = self.get_ingredients_tags()

        RecipeTag.objects.filter(recipe=instance).delete()

        recipe_tags = list()
        for tag in taglist:
            recipe_tags.append(RecipeTag(recipe=instance, tag=tag))

        RecipeTag.objects.bulk_create(recipe_tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe_ingredients = list()
        for ingredient in ingredientslist:
            recipe_ingredients.append(RecipeIngredient(
                ingredient=ingredient, recipe=instance))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return super().update(instance=instance, validated_data=validated_data)

    def get_is_in_favorited(self, obj):
        user = self.context.get('request').user
        return FavoriteList.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingList.objects.filter(
            user=user, recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'id',
            'is_subscribed',
            'recipes'
        ]

    def get_is_subscribed(self, obj):
        return obj.following.filter(
            user=self.context.get('request').user).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)[:int(self.context.get(
            'recipes_limit'))]

        ser_list = list()
        for recipe in recipes:
            ser_list.append(RecipeSerializer(recipe).data)
        return ser_list
