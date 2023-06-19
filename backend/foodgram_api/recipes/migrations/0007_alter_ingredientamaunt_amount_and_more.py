# Generated by Django 4.2.2 on 2023-06-16 10:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_favoritelist_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamaunt',
            name='amount',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'В рецепте должна быть хотябы одна еденица продукта!')]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Минимальное время готовки 1 минута!')]),
        ),
    ]