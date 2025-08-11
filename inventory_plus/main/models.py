from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases", null=True, blank=True)
   
    def __str__(self):
        return f"{self.product.name} - {self.quantity} on {self.date.strftime('%Y-%m-%d')}"

    @property
    def total_price(self):
        return self.price_at_sale * self.quantity
