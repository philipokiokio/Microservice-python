import random
from product.serializer import ProductSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Product, User
from rest_framework.response import Response
from .producer import publish

# Create your views here.


class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        serializer = ProductSerializer(Product.objects.all(), many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        publish("product_created", serializer.data)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        product = Product.objects.filter(pk=pk).first()
        if product is None:
            return Response(data={"detail": "product does not exist"}, status=404)
        serilizer = ProductSerializer(product)
        return Response(serilizer.data)

    def update(self, request, pk=None):
        product = Product.objects.filter(pk=pk).first()
        if product is None:
            return Response(data={"detail": "product does not exist"}, status=404)

        serilizer = ProductSerializer(product, data=request.data)
        serilizer.is_valid()
        serilizer.save()
        publish("product_updated", serilizer.data)

        return Response(serilizer.data)

    def destroy(self, request, pk=None):
        product = Product.objects.filter(pk=pk).first()
        if product:
            product.delete()
            publish("product_deleted", pk)

        return Response(status=204)


class UserAPIView(APIView):
    def get(self, _):
        user = random.randint(0, 40)
        return Response({"id": user})
