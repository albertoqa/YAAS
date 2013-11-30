from django.forms import widgets
from rest_framework import serializers
from YAASApp.models import auction, bid

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = auction
        fields = ('id', 'title', 'description', 'deadline', 'min_price', 'lifecycle', 'seller')

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = bid
        fields = ('id', 'amount')
