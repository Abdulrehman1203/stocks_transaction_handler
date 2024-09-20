from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import User, Stock, Transaction
from .serializers import UserSerializer, StockSerializer, TransactionSerializer
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from .authentication import jwt_required, authenticate_user
from .authentication import generate_jwt_token


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register(request):
#     username = request.data.get('username')
#     password = request.data.get('password1')
#
#     if User.objects.filter(username=username).exists():
#         return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)
#
#     # Create the user instance without the password first
#     user = User.objects.create(
#         username=username,
#     )
#
#     # Set and hash the password separately
#     user.set_password(password)
#     user.save()
#
#     # Generate JWT token
#     token = generate_jwt_token(user)
#     return Response({"message": "User registered successfully", "token": token}, status=status.HTTP_201_CREATED)
#
#
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def user_login(request):
#     username = request.data.get('username')
#
#     token = authenticate_user(username)
#     if token:
#         request.session['token'] = token
#
#     else:
#         return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_user(request):
    """
    This view handles the creation of a new user using the `POST` method.
    It validates the incoming data through the serializer and saves
    the user to the database if valid.
    """
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_username(request, username):
    """
    This view GET a user  from the database based on the provided username
    it returns the user data.
    """
    if request.method == 'GET':
        user = User.objects.get(username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_stock(request):
    """
    This view handles the creation of a new stock using the `POST` method.
    It validates the incoming data through the serializer and saves
    the stock.
    """
    if request.method == 'POST':
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_stock(request, ticker):
    """
    This view GET a stock from the database based on the provided ticker
    and returns the stock data.
    """
    if request.method == 'GET':
        stock = Stock.objects.get(ticker=ticker)
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_stocks(request):
    """
    This view GET stocks from the database and returns them.
    """
    if request.method == 'GET':
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_transaction(request):
    """
    This view handles the creation of a new transaction using the `POST` method.
    It verifies the user and stock, calculates the transaction price, and updates
    the user's balance accordingly before saving the transaction.
    """

    username = request.data.get('username')
    ticker = request.data.get('ticker')
    transaction_type = request.data.get('transaction_type')
    transaction_volume = request.data.get('transaction_volume')

    try:
        user = User.objects.get(username=username)
        stock = Stock.objects.get(ticker=ticker)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Stock.DoesNotExist:
        return Response({"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)

    transaction_price = stock.price * int(transaction_volume)

    if transaction_type == 'buy' and user.balance < transaction_price:
        return Response({"error": "You don't have enough balance to perform the transaction."},
                        status=status.HTTP_400_BAD_REQUEST)

    if transaction_type == 'buy':
        user.balance -= transaction_price
    elif transaction_type == 'sell':
        user.balance += transaction_price

    user.save()

    transaction_data = {
        'user': user.id,
        'ticker': stock.id,
        'transaction_type': transaction_type,
        'transaction_volume': transaction_volume,
        'transaction_price': transaction_price
    }

    serializer = TransactionSerializer(data=transaction_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_transactions_by_date(request, username, start_time, end_time):
    """
    This view fetches transactions for a user between two dates, using the
    `GET` method.
    """
    try:
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')

        user = User.objects.get(username=username)

        transactions = Transaction.objects.filter(
            user=user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_transactions(request, username):
    """
    This view fetches all transactions for a specific user using the `GET` method.
    """
    if request.method == 'GET':
        transactions = Transaction.objects.filter(user__username=username)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
