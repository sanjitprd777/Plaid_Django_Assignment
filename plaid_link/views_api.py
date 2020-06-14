import datetime
import json
import plaid
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import AccessToken
from .tasks import delete_transactions, fetch_transactions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from plaid_link.serializers import UserSerializer, UserLoginSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout, login
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Item
from .keys import *

client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


class UserCreate(APIView):
    """
    Creates the new user.
    """

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    User login API.
    """

    @action(methods=['POST', ], detail=False)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username,
                                password=password)
            if user is None:
                raise serializers.ValidationError(
                    "Invalid username/password. Please try again!")
            else:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    """
    User Logout API.
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        logout(request)
        data = {'success': 'Successfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)


class get_access_token(APIView):
    """
    Exchanges Public token for access token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_data = request.POST
        public_token = request_data.get('public_token')
        try:
            exchange_response = client.Item.public_token.exchange(public_token)
            serializer = AccessToken(data=exchange_response)
            if serializer.is_valid():
                access_token = serializer.validated_data['access_token']
                item = Item.objects.create(access_token=access_token,
                                           item_id=serializer.validated_data['item_id'],
                                           user=self.request.user
                                           )
                item.save()

                # Async Task
                fetch_transactions.delay(access_token)

        except plaid.errors.PlaidError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=exchange_response, status=status.HTTP_200_OK)


class get_transaction(APIView):
    """
    Retrieve transactions for credit and depository accounts.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']

            # transactions of two years i.e. 730 days
            start_date = '{:%Y-%m-%d}'.format(
                datetime.datetime.now() + datetime.timedelta(-730))
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

            try:
                transactions_response = client.Transactions.get(
                    access_token, start_date, end_date)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'transactions': transactions_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class get_identity(APIView):
    """
    Retrieve Identity information on file with the bank.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                identity_response = client.Identity.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'identity': identity_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_balance(APIView):
    """
    Gets all the information about balance of the Item.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                balance_response = client.Accounts.balance.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'balance': balance_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_item_info(APIView):
    """
    Retrieve information about an Item, like the institution, billed products,
    available products, and webhook information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                item_response = client.Item.get(access_token)
                institution_response = client.Institutions.get_by_id(
                    item_response['item']['institution_id'])
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(
                data={'error': None, 'item': item_response['item'], 'institution': institution_response['institution']},
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class get_account_info(APIView):
    """
    Retrieve high-level information about all accounts associated with an Item.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                accounts_response = client.Accounts.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'accounts': accounts_response, 'error': None, }, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
def webhook(request):
    request_data = request.POST
    webhook_type = request_data.get('webhook_type')
    webhook_code = request_data.get('webhook_code')

    if webhook_type == 'TRANSACTIONS':
        item_id = request_data.get('item_id')
        if webhook_code == 'TRANSACTIONS_REMOVED':
            removed_transactions = request_data.get('removed_transactions')
            delete_transactions.delay(item_id, removed_transactions)

        else:
            new_transactions = request_data.get('new_transactions')
            fetch_transactions.delay(None, item_id, new_transactions)

    return HttpResponse('Webhook received', status=status.HTTP_202_ACCEPTED)


def create_public_token():
    """
    Generates Public token.
    Returns : A Dictionary with keys 'public_token' and 'request_id'
    """
    url = "https://sandbox.plaid.com/sandbox/public_token/create"
    headers = {'content-type': 'application/json'}
    payload = {
        "institution_id": "ins_5",
        "public_key": PLAID_PUBLIC_KEY,
        "initial_products": ["transactions"]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    return r.json()
