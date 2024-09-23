from .models import users, Stock, Transaction
from .forms import RegisterForm
from .authentication import jwt_required, generate_jwt
from .serializers import usersSerializer, StockSerializer, TransactionSerializer, registerSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from django.contrib.auth import authenticate


@swagger_auto_schema(method='post', request_body=registerSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.data)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                username=username,
                password=make_password(password)
            )

            token = generate_jwt(user)
            return Response({"message": "User registered successfully", "token": token}, status=status.HTTP_201_CREATED)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({" Invalid request to register."}, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=registerSerializer)
@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token = generate_jwt(user)  # Make sure generate_jwt is defined

    return Response({"token": token}, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=usersSerializer)
@permission_classes([AllowAny])
@api_view(['POST'])
def add_user(request):
    """
    This view handles the creation of a new user using the `POST` method.
    It validates the incoming data through the serializer and saves
    the user to the database if valid.
    """
    if request.method == 'POST':
        serializer = usersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='GET')
@permission_classes([AllowAny])
@api_view(['GET'])
def get_user_by_username(request, username):
    """
    This view GET a user from the database based on the provided username
    it returns the user data.
    """
    user = users.objects.get(username=username)
    serializer = usersSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=StockSerializer)
@api_view(['POST'])
@jwt_required
def add_stock(request):
    """
    This view handles the creation of a new stock using the `POST` method.
    It validates the incoming data through the serializer and saves
    the stock. Requires JWT authentication.
    """
    serializer = StockSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='GET')
@permission_classes([AllowAny])
@api_view(['GET'])
def get_stock(request, ticker):
    """
    This view GET a stock from the database based on the provided ticker
    and returns the stock data. Requires JWT authentication.
    """
    stock = Stock.objects.get(ticker=ticker)
    serializer = StockSerializer(stock)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='GET')
@permission_classes([AllowAny])
@api_view(['GET'])
def get_all_stocks(request):
    """
    This view GET stocks from the database and returns them.
    Requires JWT authentication.
    """
    stocks = Stock.objects.all()
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post', request_body=TransactionSerializer)
@api_view(['POST'])
@jwt_required
def add_transaction(request):
    """
    This view handles the creation of a new transaction using the `POST` method.
    It verifies the user and stock, calculates the transaction price, and updates
    the user's balance accordingly before saving the transaction.
    """
    user_id = request.data.get('user')
    ticker = request.data.get('ticker')
    transaction_type = request.data.get('transaction_type')
    transaction_volume = request.data.get('transaction_volume')

    print("user_id =", user_id, "type:", type(user_id))  # for debugging purpose
    print("ticker =", ticker, "type:", type(ticker))  # for debugging purpose

    if user_id is None or ticker is None:
        return Response({"error": "User ID and ticker are required."}, status=400)

    try:
        user = users.objects.get(pk=user_id)
        stock = Stock.objects.get(pk=ticker)
    except users.DoesNotExist:
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
        'ticker': stock.id,  # Ensure this is the primary key
        'transaction_type': transaction_type,
        'transaction_volume': transaction_volume,
        'transaction_price': transaction_price
    }

    serializer = TransactionSerializer(data=transaction_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='GET')
@permission_classes([AllowAny])
@api_view(['GET'])
def get_transactions_by_date(request, username, start_time, end_time):
    """
    This view fetches transactions for a user between two dates, using the
    `GET` method. Requires JWT authentication.
    """
    try:
        start_date = datetime.strptime(start_time, '%Y-%m-%d')
        end_date = datetime.strptime(end_time, '%Y-%m-%d')

        user = users.objects.get(username=username)

        transactions = Transaction.objects.filter(
            user=user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='GET')
@permission_classes([AllowAny])
@api_view(['GET'])
def get_transactions(request, username):
    """
    This view fetches all transactions for a specific user using the `GET` method.
    Requires JWT authentication.
    """
    transactions = Transaction.objects.filter(user__username=username)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
