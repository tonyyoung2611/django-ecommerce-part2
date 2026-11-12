
"""
Views for the Django eCommerce application.

This module handles product listings, shopping carts, checkout,
user registration, product reviews, vendor management, and
the Reddit feed integration.
"""

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import ProtectedError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm, RegistrationForm, ReviewForm, StoreForm
from .functions.reddit import get_reddit_posts
from .models import Order, OrderItem, Product, Profile, Store


def product_list(request):
    """Display all available products on the storefront."""
    products = Product.objects.all()

    return render(
        request,
        'shop/product_list.html',
        {'products': products}
    )


def view_cart(request):
    """Display products, quantities, subtotals, and the cart total."""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()

        if product:
            subtotal = product.price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

            total += subtotal

    return render(
        request,
        'shop/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


def add_to_cart(request, product_id):
    """Add one product to the session cart if stock is available."""
    if request.method != 'POST':
        return redirect('product_list')

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    product_key = str(product.id)

    current_quantity = cart.get(product_key, 0)

    # Prevent customers from adding more items than available.
    if current_quantity < product.stock:
        cart[product_key] = current_quantity + 1
        request.session['cart'] = cart

    return redirect('view_cart')


def remove_from_cart(request, product_id):
    """Remove a product from the customer's session cart."""
    if request.method != 'POST':
        return redirect('view_cart')

    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart

    return redirect('view_cart')


@login_required
def checkout(request):
    """
    Process checkout for buyers and create an order.

    Validate cart quantities and lock product records during
    checkout to reduce the risk of overselling products.
    """
    if request.method != 'POST':
        return redirect('view_cart')

    # Only registered buyers may complete purchases.
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'buyer'
    ):
        return HttpResponseForbidden(
            "Only buyers can checkout."
        )

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('view_cart')

    # Keep order creation and stock updates in one transaction.
    with transaction.atomic():
        products = Product.objects.select_for_update().filter(
            id__in=cart.keys()
        )

        product_map = {
            str(product.id): product
            for product in products
        }

        total = 0

        # Validate all items before creating the order.
        for product_id, quantity in cart.items():
            product = product_map.get(product_id)

            if (
                product is None
                or type(quantity) is not int
                or quantity <= 0
                or quantity > product.stock
            ):
                return redirect('view_cart')

            total += product.price * quantity

        order = Order.objects.create(
            buyer=request.user,
            total=total
        )

        # Record purchased items and reduce inventory.
        for product_id, quantity in cart.items():
            product = product_map[product_id]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            product.stock -= quantity
            product.save(update_fields=['stock'])

    # Clear the cart after the database transaction succeeds.
    request.session['cart'] = {}

    invoice = "Thank you for your purchase!\n\n"
    invoice += f"Order Number: {order.id}\n\n"
    invoice += "Items Purchased:\n"

    for item in order.items.all():
        invoice += (
            f"{item.product.name} - "
            f"Quantity: {item.quantity} - "
            f"Price: ${item.price}\n"
        )

    invoice += f"\nTotal: ${order.total}"

    # Send the buyer an invoice using the configured email backend.
    send_mail(
        subject=f"Invoice for Order #{order.id}",
        message=invoice,
        from_email="store@example.com",
        recipient_list=[request.user.email],
        fail_silently=False
    )

    return redirect(
        'order_confirmation',
        order_id=order.id
    )


def register(request):
    """Register a new buyer or vendor and log them in."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Store the selected account role in the user profile.
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role']
            )

            login(request, user)
            return redirect('product_list')
    else:
        form = RegistrationForm()

    return render(
        request,
        'shop/register.html',
        {'form': form}
    )


@login_required
def order_confirmation(request, order_id):
    """Display an order confirmation to its buyer only."""
    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user
    )

    return render(
        request,
        'shop/order_confirmation.html',
        {'order': order}
    )


@login_required
def add_review(request, product_id):
    """Allow a signed-in user to submit a product review."""
    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)

            review.product = product
            review.user = request.user

            # Mark reviews as verified when the user purchased
            # the product in a previous order.
            review.verified_purchase = OrderItem.objects.filter(
                order__buyer=request.user,
                product=product
            ).exists()

            review.save()
            return redirect('product_list')
    else:
        form = ReviewForm()

    return render(
        request,
        'shop/add_review.html',
        {
            'form': form,
            'product': product
        }
    )


@login_required
def vendor_dashboard(request):
    """Display stores and products owned by the current vendor."""
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can access this page."
        )

    stores = Store.objects.filter(
        owner=request.user
    )

    return render(
        request,
        'shop/vendor_dashboard.html',
        {'stores': stores}
    )


@login_required
def create_store(request):
    """Allow vendors to create stores under their accounts."""
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can create stores."
        )

    if request.method == 'POST':
        form = StoreForm(request.POST)

        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()

            return redirect('vendor_dashboard')
    else:
        form = StoreForm()

    return render(
        request,
        'shop/create_store.html',
        {'form': form}
    )


@login_required
def create_product(request):
    """Allow vendors to add products to stores they own."""
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can create products."
        )

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():
            product = form.save(commit=False)

            # Prevent vendors from adding products to other stores.
            if product.store.owner_id != request.user.id:
                return HttpResponseForbidden(
                    "You do not own this store."
                )

            product.save()
            return redirect('vendor_dashboard')

    else:
        form = ProductForm(
            user=request.user
        )

    return render(
        request,
        'shop/create_product.html',
        {'form': form}
    )


@login_required
def edit_product(request, product_id):
    """Allow vendors to edit products belonging to their stores."""
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can edit products."
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        store__owner=request.user
    )

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            instance=product,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')

    else:
        form = ProductForm(
            instance=product,
            user=request.user
        )

    return render(
        request,
        'shop/edit_product.html',
        {
            'form': form,
            'product': product
        }
    )


@login_required
def delete_product(request, product_id):
    """
    Allow vendors to delete their products.

    Products referenced by existing orders cannot be deleted
    when protected by the database relationship.
    """
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can delete products."
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        store__owner=request.user
    )

    if request.method == 'POST':
        try:
            product.delete()
            return redirect('vendor_dashboard')

        except ProtectedError:
            # Preserve products referenced by existing orders.
            return render(
                request,
                'shop/delete_product.html',
                {
                    'product': product,
                    'error': (
                        "This product cannot be deleted "
                        "because it belongs to an existing order."
                    )
                }
            )

    return render(
        request,
        'shop/delete_product.html',
        {'product': product}
    )


@login_required
def edit_store(request, store_id):
    """Allow vendors to edit stores belonging to their accounts."""
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can edit stores."
        )

    store = get_object_or_404(
        Store,
        id=store_id,
        owner=request.user
    )

    if request.method == 'POST':
        form = StoreForm(
            request.POST,
            instance=store
        )

        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')

    else:
        form = StoreForm(
            instance=store
        )

    return render(
        request,
        'shop/edit_store.html',
        {
            'form': form,
            'store': store
        }
    )


@login_required
def delete_store(request, store_id):
    """
    Allow vendors to delete stores they own.

    Handle protected products that belong to existing orders.
    """
    if (
        not hasattr(request.user, 'profile')
        or request.user.profile.role != 'vendor'
    ):
        return HttpResponseForbidden(
            "Only vendors can delete stores."
        )

    store = get_object_or_404(
        Store,
        id=store_id,
        owner=request.user
    )

    if request.method == 'POST':
        try:
            store.delete()
            return redirect('vendor_dashboard')

        except ProtectedError:
            # Display an error instead of deleting order history.
            return render(
                request,
                'shop/delete_store.html',
                {
                    'store': store,
                    'error': (
                        "This store cannot be deleted "
                        "because one or more products "
                        "belong to existing orders."
                    )
                }
            )

    return render(
        request,
        'shop/delete_store.html',
        {'store': store}
    )


def reddit_feed(request):
    """Display Python-related Reddit posts on the Reddit feed page."""
    posts = get_reddit_posts('python')

    return render(
        request,
        'shop/reddit_feed.html',
        {'posts': posts}
    )
