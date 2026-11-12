from rest_framework import serializers
from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'description']
        read_only_fields = ['owner']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock']

    def validate_store(self, store):
        user = self.context['request'].user

        if store.owner_id != user.id:
            raise serializers.ValidationError(
                "You can only add products to your own stores."
            )

        return store


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = [
            'id',
            'product',
            'username',
            'rating',
            'comment',
            'verified_purchase',
            'created_at'
        ]