from django.db import models
import os

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="reservations"
    )
    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, related_name="reservations"
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reservation_date} - {self.store.name}"