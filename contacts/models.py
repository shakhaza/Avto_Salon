from django.db import models
from datetime import datetime
from cars.models import Car
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    customer_need = models.CharField(max_length=100)
    car_title = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    create_date = models.DateTimeField(blank=True, default=datetime.now)

    def __str__(self):
        return self.email
