from django.db import models


class recipes(models.Model):
    name = models.CharField(max_length=100)
    
