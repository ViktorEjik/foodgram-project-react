import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (FavoriteList, Ingredient, IngredientAmaunt, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingRecipeList,
                            Tag, User)


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
        model = IngredientAmaunt
        fields = ('ingredient', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)

    author = UserSerializer(read_only=True)

    ingredients = IngredientAmountSerializer(many=True, read_only=True)

    is_in_favorite = serializers.SerializerMethodField()

    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'ingredients',
                  'name', 'author', 'text',
                  'cooking_time', 'image',
                  'is_in_favorite', 'is_in_shopping_cart']

    def get_is_in_favorite(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return FavoriteList.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return ShoppingRecipeList.objects.filter(
            user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    author = UserSerializer(read_only=True)

    ingredients = IngredientAmountSerializer(many=True, read_only=True)

    image = Base64ImageField()

    is_in_favorite = serializers.SerializerMethodField()

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
                  'is_in_favorite', 'is_in_shopping_cart']

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeTag.objects.filter(recipe=instance).delete()

        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=instance)

        instance.image = validated_data.pop('image', instance.image)
        instance.text = validated_data.pop('text', instance.text)
        instance.name = validated_data.pop('text', instance.name)
        instance.cooking_time = validated_data.pop(
            'text', instance.cooking_time)
        instance.save()
        return instance

    def get_is_in_favorite(self, obj):
        user = self.context.get('request').user
        return FavoriteList.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingRecipeList.objects.filter(
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
