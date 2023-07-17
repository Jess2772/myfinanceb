from django.shortcuts import render
from . models import *
from rest_framework.response import Response
from . serializer import *
import sys

from django.contrib.auth import get_user_model, login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from rest_framework import permissions, status
from .validations import *


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


class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	##
	def get(self, request):
		serializer = UserSerializer(request.user)
		response = Response({'user': serializer.data}, status=status.HTTP_200_OK)
		return response
	
class CategoryRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = validate_category(request.data)
		serializer = CategoryRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			category = serializer.create(clean_data)
			if category:
				response = Response(serializer.data, status=status.HTTP_201_CREATED)
				return response
		return Response(status=status.HTTP_400_BAD_REQUEST)