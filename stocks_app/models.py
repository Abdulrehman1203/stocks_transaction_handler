from django.utils import timezone
from django.db import models


class users(models.Model):
    """
    This model stores basic information about the user, including their username
    and balance. Each user can have multiple transactions associated with them.

    Fields:
        - username: A name for the user.
        - balance: The initial balance of the user.
    """
    username = models.CharField(max_length=50)
    balance = models.IntegerField()

    def __str__(self):
        return self.username


class Stock(models.Model):
    """
    This model contains details about a stock, including its ticker symbol
    and price.

    Fields:
        - ticker: The stock ticker symbol
        - price: The current price of the stock.
    """
    ticker = models.CharField(max_length=50)
    price = models.FloatField()

    def __str__(self):

        return self.ticker


class Transaction(models.Model):
    """
    This model stores information about a transaction of a stock.
    A transaction can be a 'buy' or 'sell' type and contains
    details about the transaction volume, price, and the created time.

    Fields:
        - user: The user who performed the transaction (ForeignKey User).
        - ticker: The stock involved in the transaction (ForeignKey Stock).
        - transaction_type: The type of transaction, 'buy' or 'sell'.
        - transaction_volume: The number of stocks quantity involved in the transaction.
        - transaction_price: The total price of the transaction.
        - created_at: The time when the transaction was created.
    """
    BUY = 'buy'
    SELL = 'sell'

    Transaction_type = [
        (BUY, 'buy'),
        (SELL, 'sell'),
    ]
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    ticker = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=5, choices=Transaction_type)
    transaction_volume = models.IntegerField()
    transaction_price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.transaction_type} - {self.ticker}'
