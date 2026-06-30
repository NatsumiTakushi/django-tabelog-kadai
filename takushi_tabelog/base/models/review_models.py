from django.db import models
import os

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="reviews"
    )
    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name