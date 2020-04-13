from rest_framework import serializers, viewsets

from .models import Order, OrderLine

class OrderLineSerializer(serializers.HyperlinkedModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderLine
        fields = ('id', 'order', 'product', 'status')
        read_only_fields = ('id', 'order', 'product')


class PaidOrderLineViewSet(viewsets.ModelViewSet):
    queryset = OrderLine.objects.filter(order__status=Order.PAID).order_by("-order__date_added")
    serializer_class = OrderLineSerializer
    filter_fields = ('order','status')


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ('shipping_name',
                  'shipping_address1',
                  'shipping_address2',
                  'shipping_zipcode',
                  'shipping_city',
                  'shipping_country',
                  'date_updated',
                  'date_added')

class PaidOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.filter(status=Order.PAID).order_by("-date_added")
    serializer_class = OrderSerializer



# curl -u dispatch@booktime.domain:django1234 -H 'Content-Type: application/json' -H 'Accept: application/json; indent=4' -XPUT -d '{"status": 20}' http://127.0.0.1:8000/api/orderlines/5/