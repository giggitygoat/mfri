from .models import Recipe
from .models import Ingredient
from django.contrib import admin


admin.site.register(Recipe)
admin.site.register(Ingredient)                                  

#r Register your models here.
