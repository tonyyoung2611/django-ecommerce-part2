
"""Database models for the Django eCommerce application.

This module defines stores, products, user profiles, orders,
order items, and customer reviews.
"""

from django.conf import settings
from django.db import models


class Store(models.Model):
    """Represent a store owned by a registered user."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Deleting the owner also deletes their stores.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Return the store name."""
        return self.name


class Product(models.Model):
    """Represent a product listed for sale in a store."""

    # Each product belongs to one store.
    # The related name allows access through store.products.
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    # DecimalField stores prices without floating-point rounding.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Stock cannot be stored as a negative integer.
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return the product name."""
        return self.name


class Profile(models.Model):
    """Store the role associated with a registered user."""

    ROLE_CHOICES = [
        ('vendor', 'Vendor'),
        ('buyer', 'Buyer'),
    ]

    # Each user has at most one profile.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # New profiles are assigned the buyer role by default.
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='buyer'
    )

    def __str__(self):
        """Return the username and assigned role."""
        return f"{self.user.username} - {self.role}"


class Order(models.Model):
    """Represent a completed purchase made by a buyer."""

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Automatically record when the order is created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Store the total amount charged for the order.
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        """Return the order number and buyer username."""
        return f"Order #{self.id} - {self.buyer.username}"


class OrderItem(models.Model):
    """Represent an individual product purchased in an order."""

    # An order can contain multiple purchased products.
    # The related name allows access through order.items.
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # PROTECT prevents deletion of a product referenced by an
    # order item, preserving the product relationship in order history.
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    # Save the product price at the time of purchase.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        """Return the purchased product name and quantity."""
        return f"{self.product.name} x {self.quantity}"


class Review(models.Model):
    """Represent a customer's review of a product."""

    # Each product can have multiple customer reviews.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    rating = models.PositiveIntegerField()
    comment = models.TextField()

    # The review creation view determines whether the customer
    # previously purchased this product.
    verified_purchase = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """Return the reviewer's username and product name."""
        return f"{self.user.username} - {self.product.name}"
