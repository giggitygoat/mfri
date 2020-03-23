from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

class Token(models.Model):
    identi = models.CharField(max_length=255, unique=True)

# Create your models here.
