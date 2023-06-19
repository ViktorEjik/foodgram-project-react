from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
    )

    first_name = models.CharField(
        max_length=150,
    )

    last_name = models.CharField(
        max_length=150,
    )

    role = models.CharField(
        'роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique relation'
            )
        ]


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
    )

    colore = models.CharField(
        max_length=7,
    )

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
    )

    measurement_unit = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return self.name


class IngredientAmaunt(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(
            1, 'В рецепте должна быть хотябы одна еденица продукта!'),)
    )

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=200,
    )

    text = models.TextField()

    cooking_time = models.IntegerField(
        validators=(MinValueValidator(
            1, 'Минимальное время готовки 1 минута!'),)
    )

    image = models.ImageField(
        upload_to='images',
    )

    ingredients = models.ManyToManyField(
        IngredientAmaunt,
        through='RecipeIngredient',
        blank=False
    )

    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        blank=False
    )

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        IngredientAmaunt,
        on_delete=models.CASCADE
    )


class FavoriteList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoritelist'
    )


class ShoppingIngredientList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_ingredient_list'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient}'


class ShoppingRecipeList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_recipe_list'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe_list'
    )
