# Generated by Django 4.2.2 on 2023-06-23 20:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_ingredientamaunt_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to='recipes.recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='shoppingrecipelist',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='shoppingrecipelist',
            name='user',
        ),
        migrations.DeleteModel(
            name='ShoppingIngredientList',
        ),
        migrations.DeleteModel(
            name='ShoppingRecipeList',
        ),
    ]