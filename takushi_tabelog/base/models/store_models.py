from django.db import models
from django.utils.crypto import get_random_string
import os
 
 
def create_id():
    return get_random_string(22)
 
 
def upload_image_to(instance, filename):
    store_id = instance.id
    return os.path.join('static', 'stores', store_id, filename)

class Tag(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)
 
    def __str__(self):
        return self.name

class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Store(models.Model):
    id = models.CharField(default=create_id, primary_key=True,
                          max_length=22, editable=False)
    name = models.CharField(default='', max_length=50)
    image = models.ImageField(default="", blank=True,
                              upload_to=upload_image_to)
    description = models.TextField(default='', blank=True)
    lower_price = models.PositiveIntegerField(default=0)
    upper_price = models.PositiveIntegerField(default=0)
    open_hours = models.CharField(default='', max_length=50)
    zip_code = models.CharField(default='', max_length=50)
    address = models.CharField(default='', max_length=100)
    phone_number = models.CharField(default='', max_length=50)
    holiday = models.CharField(default='', max_length=20)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
 
    def __str__(self):
        return self.name