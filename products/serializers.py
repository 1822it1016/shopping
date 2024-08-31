from rest_framework import serializers
from .models import Product
from .constants import POSITIVE_FIELDS_OF_PRODUCT
from .utils import validate_non_negative


class ProductSerializer(serializers.ModelSerializer):
    """
    serializer for serializing the data as per the Product
    """

    class Meta:
        model = Product
        fields = ['id', 'product_id', 'product_name', 'category', 'price', 'quantity_sold', 'rating', 'review_count']

    def to_internal_value(self, data):
        fields_to_validate = POSITIVE_FIELDS_OF_PRODUCT

        for field in fields_to_validate:
            validate_non_negative(data.get(field), field)

        return super().to_internal_value(data)
