from django.shortcuts import render
from . models import *
from rest_framework.response import Response
from . serializer import *
import sys

from django.contrib.auth import get_user_model, login, logout, _get_user_session_key
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from rest_framework import permissions, status
from .validations import *
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.forms.models import model_to_dict
import jwt
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
class UserRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			print("valid credentials, registering")
			sys.stdout.flush()
			user = serializer.create(clean_data)
			if user:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	@csrf_exempt
	@method_decorator(ensure_csrf_cookie)
	def post(self, request):
		data = request.data
		assert validate_email(data)
		assert validate_password(data)
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.check_user(data)
			print("Sending login request")
			sys.stdout.flush()
			login(request, user)
			response = Response({'user': serializer.data}, status=status.HTTP_200_OK)
			return response
		

class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)

class LogoutView(APIView):     
	permission_classes = (permissions.IsAuthenticated,)    
	def post(self, request):
		try:               
			refresh_token = request.data["refresh_token"]              
			token = RefreshToken(refresh_token)               
			token.blacklist()               
			return Response(status=status.HTTP_205_RESET_CONTENT)          
		except Exception as e:  
			print(e)             
			return Response(status=status.HTTP_400_BAD_REQUEST)	

class UserTest(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def get(self, request):
		user = UserModel.objects.get(user_id=_get_user_session_key(request))
		serializer = UserSerializer(user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	@method_decorator(ensure_csrf_cookie)
	def get(self, request):
		serializer = UserSerializer(request.user)
		response = Response({'user': serializer.data}, status=status.HTTP_200_OK)
		return response

class HomeView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self, request):       
			content = {'message': 'Still a work in progress....'}   
			return Response(content)

class CategoryRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		serializer = CategoryRegisterSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			category = serializer.create(request.data)
			if category:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)
	

class BudgetRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		user_id = request.data['user_id']
		serializer = BudgetRegisterSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			Budget.objects.filter(user_id = user_id, is_active = 'Y').update(is_active = 'N', eff_to = datetime.now(tz=timezone.utc))
			budget = serializer.create(request.data, user_id)
			# TODO: need to ensure that mandatory fields are populated, because cannot reinforce in models.py
			if budget:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)
	
@method_decorator(ensure_csrf_cookie, name='dispatch')
class TransactionRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)

	def post(self, request):
		user_id = _get_user_session_key(request)
		merchant = Merchant.objects.get(merchant_name = request.data['merchant'])
		category_id = merchant.category_id
		merchant_id = merchant.merchant_id
		serializer = TransactionRegisterSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			transaction = serializer.create(request.data, user_id, category_id, merchant_id)
			# TODO: need to ensure that mandatory fields are populated, because cannot reinforce in models.py
			if transaction:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)


class MerchantRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		category_id = Categories.objects.get(name = request.data['category']).category_id
		serializer = MerchantRegisterSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			merchant = serializer.create(request.data, category_id)
			# TODO: need to ensure that mandatory fields are populated, because cannot reinforce in models.py
			if merchant:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)


class UserBudget(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		user_id = request.data['user_id']
		try:
			budget = Budget.objects.get(user_id = user_id, is_active = 'Y')
			##rsp = json.loads(serialize('json', budget), many=False)
			return Response(model_to_dict(budget), status=status.HTTP_200_OK)
		except Budget.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		
class UserTransaction(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		user_id = request.data['user_id']
		category = request.data['category']
		merchant = request.data['merchant']
		category_id = Categories.objects.get_or_create(name=category)[0].category_id
		merchant_id = Merchant.objects.get_or_create(merchant_name=merchant, category=Categories(category_id=category_id))[0].merchant_id
		serializer = TransactionRegisterSerializer(data=request.data)
		sys.stdout.flush()
		if serializer.is_valid(raise_exception=True):
			transaction = serializer.create(request.data, user_id, category_id, merchant_id)
			return Response(status=status.HTTP_200_OK)
		return Response({"detail": "Error when saving record"}, status=status.HTTP_400_BAD_REQUEST)


class UserSpending(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		pymt = {"CC": "Credit Card", "DC": "Debit Card", "CH": "Cash"}
		user_id = request.data['user_id']
		try:
			transactions = Transaction.objects.filter(user_id = user_id).values()
			for transaction in transactions:
				transaction['category'] = Categories.objects.get(category_id=transaction['category_id']).name
				transaction['merchant'] = Merchant.objects.get(merchant_id=transaction['merchant_id']).merchant_name
				transaction['pymt_method_full'] = pymt[transaction['pymt_method']]
			return Response(transactions, status=status.HTTP_200_OK)
		except:
			return Response(status=status.HTTP_404_NOT_FOUND)