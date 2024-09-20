from rest_framework import serializers
from .models import User, Stock, Transaction


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is for the user's `username` and `balance`
    fields, allowing them to be read and written in API responses and requests.
    """
    class Meta:
        model = User
        fields = ['username', 'balance']


class StockSerializer(serializers.ModelSerializer):
    """
    This serializer handles the `ticker` and `price` fields of the stock, which can be used
    for creating or retrieving stock data through API requests.
    """
    class Meta:
        model = Stock
        fields = ['ticker', 'price']


class TransactionSerializer(serializers.ModelSerializer):
    """
    This serializer includes fields related to a transaction such as the user who
    made the transaction, the stock involved, transaction type, price, volume, and
    creation date.

    """
    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'ticker',
            'transaction_type',
            'transaction_price',
            'transaction_volume',
            'created_at',
        ]
