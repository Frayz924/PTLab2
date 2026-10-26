from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    person = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
class CartItem(models.Model):
    session_key = models.CharField(max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"