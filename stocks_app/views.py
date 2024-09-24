from .forms import RegisterForm
from .models import users, Stock, Transaction
from .authentication import jwt_required, generate_jwt
from .serializers import usersSerializer, StockSerializer, TransactionSerializer, registerSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from datetime import datetime


""" 
This CBV handles the user registration process  using the `POST` method.
It accepts the incoming user credentials and generate token for
user.
"""


class User_RegisterView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to create a new user using the `POST` method.
        @:param request : which contained the user inputted data
    """
    @swagger_auto_schema(request_body=registerSerializer)
    def post(self, request):
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


""" 
This CBV handles the user login process  using the `POST` method.
It validates the incoming user credentials and generate token for
user authentication.
"""


class User_LoginView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to create a new user using the `POST` method.
        @:param request : which contained the user inputted data
    """
    @swagger_auto_schema(request_body=registerSerializer)
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        token = generate_jwt(user)
        return Response({"token": token}, status=status.HTTP_200_OK)


""" 
This CBV handles the creation of a new user using the `POST` method.
It validates the incoming data through the serializer and saves,
the user to the database if valid.
"""


class Add_UserView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to create a new user using the `POST` method.
        @:param request : which contained the user inputted data
    """

    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=usersSerializer)
    def post(self, request):
        serializer = usersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
This CBV GET a user from the database based on the provided username
it returns the user data.
"""


class GetUser_ByUsernameView(APIView):
    permission_classes = [AllowAny]
    """
        This method is used to GET user info using the `GET` method.
        @:param request : which contained the user inputted data
    """
    @method_decorator(jwt_required)
    @swagger_auto_schema()
    def get(self, request, username):
        try:
            user = users.objects.get(username=username)
            serializer = usersSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


"""
This CBV handles the creation of a new stock using the `POST` method.
It validates the incoming data through the serializer and saves
the stock. Requires JWT authentication.
"""


class Add_StockView(APIView):
    permission_classes = [AllowAny]
    """
        This method is used to add a new Stock using the `POST` method.
        @:param request : which contained the user inputted data

    """

    @swagger_auto_schema(request_body=StockSerializer)
    @method_decorator(jwt_required)
    def post(self, request):
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
This CBV GET a stock from the database based on the provided ticker
and returns the stock data. Requires JWT authentication.
"""


class Get_StockView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to get Stock info using the `GET` method.
        @:param request : which contained the user inputted data
        @:param ticker : which represents the stock symbol

    """
    
    @method_decorator(jwt_required)
    @swagger_auto_schema()
    def get(self, request, ticker):
        try:
            stock = Stock.objects.get(ticker=ticker)
            serializer = StockSerializer(stock)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)


"""
This CBV GET stocks from the database and returns them.
"""


class Get_AllStocksView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to view all the stocks using the `POST` method.
        @:param request : which contained the user inputted data
    """

    @swagger_auto_schema()
    @method_decorator(jwt_required)
    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


"""
This CBV handles the creation of a new transaction using the `POST` method.
It verifies the user and stock, calculates the transaction price, and updates
the user's balance accordingly before saving the transaction.
"""


class Add_TransactionView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to create a new transaction  `POST` method.
        @:param request : which contained the user inputted data
    """

    @swagger_auto_schema(request_body=TransactionSerializer)
    @method_decorator(jwt_required)
    def post(self, request):
        user_id = request.data.get('user')
        ticker = request.data.get('ticker')
        transaction_type = request.data.get('transaction_type')
        transaction_volume = request.data.get('transaction_volume')

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


"""
This CBV fetches transactions for a user between two dates, using the
`GET` method. Requires JWT authentication.
"""


class Get_TransactionsByDateView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to view the transactions created by user in certain period of time using the `GET` method.
        @:param request : which contained the user inputted data
        @:param username : which represents the username of the user
        @:param start_time : which represents the starting time of the transaction
        @:param end_time : which represents the ending time of the transaction
    """

    @swagger_auto_schema()
    @method_decorator(jwt_required)
    def get(self, request, username, start_time, end_time):
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


"""
This CBV fetches all transactions for a specific user using the `GET` method.
"""


class Get_TransactionsView(APIView):
    permission_classes = [AllowAny]

    """
        This method is used to view the transactions created by user in certain period using the `GET` method.
        @:param request : which contained the user inputted data
        @:param username : which represents the username of the user
    """

    @swagger_auto_schema()
    @method_decorator(jwt_required)
    def get(self, request, username):
        transactions = Transaction.objects.filter(user__username=username)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
