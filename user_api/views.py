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
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@ensure_csrf_cookie
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

@ensure_csrf_cookie
class UserLogin(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
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
@ensure_csrf_cookie
class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)
	
@ensure_csrf_cookie
class UserTest(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def get(self, request):
		user = UserModel.objects.get(user_id=_get_user_session_key(request))
		serializer = UserSerializer(user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)

@ensure_csrf_cookie
class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	def get(self, request):
		serializer = UserSerializer(request.user)
		response = Response({'user': serializer.data}, status=status.HTTP_200_OK)
		return response

@ensure_csrf_cookie
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
	
@ensure_csrf_cookie
class BudgetRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = (SessionAuthentication,)
	def post(self, request):
		user_id = _get_user_session_key(request)
		serializer = BudgetRegisterSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			Budget.objects.filter(user_id = user_id, is_active = 'Y').update(is_active = 'N', eff_to = datetime.now(tz=timezone.utc))
			budget = serializer.create(request.data, user_id)
			# TODO: need to ensure that mandatory fields are populated, because cannot reinforce in models.py
			if budget:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)
	
@ensure_csrf_cookie
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

@ensure_csrf_cookie
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