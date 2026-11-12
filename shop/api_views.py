from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Store, Product
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ReviewSerializer,
)


def is_vendor(user):
    return (
        hasattr(user, 'profile')
        and user.profile.role == 'vendor'
    )


# Get stores belonging to a vendor
@api_view(['GET'])
def vendor_stores(request, vendor_id):
    get_object_or_404(get_user_model(), pk=vendor_id)

    stores = Store.objects.filter(owner_id=vendor_id)
    serializer = StoreSerializer(stores, many=True)

    return Response(serializer.data)


# Get products belonging to a store
@api_view(['GET'])
def store_products(request, store_id):
    store = get_object_or_404(Store, pk=store_id)

    products = Product.objects.filter(store=store)
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


# Vendors can retrieve reviews for their products
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def product_reviews(request, product_id):
    if not is_vendor(request.user):
        return Response(
            {'error': 'Only vendors can retrieve reviews.'},
            status=status.HTTP_403_FORBIDDEN
        )

    product = get_object_or_404(Product, pk=product_id)

    if product.store.owner_id != request.user.id:
        return Response(
            {'error': 'You can only view reviews for your products.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ReviewSerializer(
        product.reviews.all(),
        many=True
    )

    return Response(serializer.data)


# Vendors can create stores through the API
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_create_store(request):
    if not is_vendor(request.user):
        return Response(
            {'error': 'Only vendors can create stores.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = StoreSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(owner=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# Vendors can add products to their own stores
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_create_product(request):
    if not is_vendor(request.user):
        return Response(
            {'error': 'Only vendors can create products.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )