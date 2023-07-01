from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint


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
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
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


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=200
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=60,
        db_index=True,
        unique=True
    )
    color = ColorField(
        format='hex',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Проверьте вводимый формат',
            )]
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name', )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/image/',
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )
    cooking_time = models.BigIntegerField()

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return self.name


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'


class ShoppingCart(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, 'Минимальное количество ингредиента 1!')],
    )

    class Meta:
        ordering = ('-id', )

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount} '
        )
