from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=19, blank=True, help_text="XXXX XXXX XXXX XXXX")
    card_expiry = models.CharField(max_length=5, blank=True, help_text="MM/YY")
    card_holder = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Purchase(models.Model):
    PAYMENT_CHOICES = (
        ('FULL', 'Paid in Full'),
        ('INSTALLMENT', 'Installment Plan'),
    )
    
    INSTALLMENT_PERIODS = (
        (12, '12 Months'),
        (24, '24 Months'),
    )

    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('ACTIVE', 'Active Installment'),
        ('COMPLETED', 'Completed Installment'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    final_price = models.IntegerField()
    installment_months = models.IntegerField(choices=INSTALLMENT_PERIODS, null=True, blank=True)
    
    @property
    def monthly_payment(self):
        if self.payment_type == 'INSTALLMENT' and self.installment_months:
            return self.final_price / self.installment_months
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.car.car_title if self.car else 'Unknown Car'}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
