from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=256)
    logo = models.ImageField(upload_to="images/suppliers/", default="images/default_supplier.jpg")
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=512)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to="images/products/", default="images/default_product.jpg")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    suppliers = models.ManyToManyField('Supplier', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_low_stock_notified = models.DateTimeField(blank=True, null=True)
    last_expiry_notified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.localdate()
        return delta.days

    def get_absolute_url(self):
        return reverse("inventory:product_detail_view", args=[self.id])