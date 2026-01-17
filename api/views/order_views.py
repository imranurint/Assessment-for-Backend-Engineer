from rest_framework import viewsets, permissions, response, status
from api.models import Order
from api.serializers.order import OrderSerializer, OrderCreateSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options'] 

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        read_serializer = OrderSerializer(order)
        return response.Response(read_serializer.data, status=status.HTTP_201_CREATED)

