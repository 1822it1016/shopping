from django.db import models


class Product(models.Model):
    """
    model for storing the data of the sheet for a product
    """
    id = models.BigAutoField(primary_key=True)
    product_id = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.FloatField()
    quantity_sold = models.IntegerField()
    rating = models.FloatField()
    review_count = models.IntegerField()

    def __str__(self):
        return self.product_name
