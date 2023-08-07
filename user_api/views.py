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
from django.db.models import Sum, Count
import datetime
from datetime import date, datetime

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

class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	@method_decorator(ensure_csrf_cookie)
	def get(self, request):
		serializer = UserSerializer(request.user)
		response = Response({'user': serializer.data}, status=status.HTTP_200_OK)
		return response

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
			return Response(model_to_dict(budget), status=status.HTTP_200_OK)
		except Budget.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		
class UserTransaction(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		user_id = request.data['user_id']
		category = request.data['category']
		merchant = request.data['merchant']
		category_id = Categories.objects.get_or_create(category_name=category)[0].category_id
		merchant_id = Merchant.objects.get_or_create(merchant_name=merchant, category=Categories(category_id=category_id))[0].merchant_id
		serializer = TransactionRegisterSerializer(data=request.data)
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
			transactions = Transaction.objects.filter(user_id = user_id).order_by('-transaction_date').values()
			for transaction in transactions:
				transaction['category'] = Categories.objects.get(category_id=transaction['category_id']).category_name
				transaction['merchant'] = Merchant.objects.get(merchant_id=transaction['merchant_id']).merchant_name
				transaction['pymt_method_full'] = pymt[transaction['pymt_method']]
			return Response(transactions, status=status.HTTP_200_OK)
		except:
			return Response(status=status.HTTP_404_NOT_FOUND)
		

class UserSpendingByCategory(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		user_id = request.data['user_id']
		date_from = request.data['date_from']
		date_to = request.data['date_to']
		categories = request.data['category_names']
		amountByCategory = []
		countByCategory = []
		merchantCountByCategory = []
	
		for category in categories:
			amount = {}
			count = {}
			merchant = {}
			category_id = Categories.objects.get(category_name=category).category_id
			amount['id'] = count['id'] = merchant['id'] = category_id
			amount['label'] = count['label'] = merchant['label'] = category 
	
			try:
				transactions = Transaction.objects.filter(user_id=user_id, transaction_date__gte=date_from, transaction_date__lte=date_to, category_id=category_id)
				numTransactions = transactions.count()
				topMerchant = transactions.values('merchant_id').annotate(total=Count('merchant_id')).order_by('-total')[0]
				topMerchantName = Merchant.objects.get(merchant_id=topMerchant['merchant_id']).merchant_name
				
				if (numTransactions == 0):
					amount['value'] = count['value'] = merchant['value'] = 0

				else:
					tot_amount = transactions.aggregate(s=Sum('amount'))['s']
					amount['value'] = tot_amount
					count['value'] = numTransactions
					merchant['label'] = topMerchantName
					merchant['value'] = topMerchant['total']
					
			except:
				amount['value'] = count['value'] = merchant['value'] = 0

			amountByCategory.append(amount)
			countByCategory.append(count)
			merchantCountByCategory.append(merchant)

		return Response({'amountByCategory': amountByCategory, 'countByCategory': countByCategory, 'merchantCountByCategory': merchantCountByCategory}, status=status.HTTP_200_OK)


class UserMonthSpending(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def post(self, request):
		pymt = {"CC": "Credit Card", "DC": "Debit Card", "CH": "Cash"}
		categories = ["Grocery", "Healthcare", "Dining", "Clothing", "Miscellaneous", "Housing", "Utility", "Transportation", "Entertainment"] 
		today = date.today()
		month = today.month
		year = today.year
		user_id = request.data['user_id']
		rsp = {}
		for c in categories:
			category_id = Categories.objects.get(category_name=c).category_id
			categoryData = {'spentThisMonth': 0, 'transactions': []}
			try:
				# name of category, amount spent this month, transactions for this month
				transactions = Transaction.objects.filter(user_id = user_id, category_id=category_id, transaction_date__month=month, transaction_date__year=year).order_by('-transaction_date')
				amount = transactions.aggregate(s=Sum('amount'))['s']
				if (amount == None):
					categoryData['spentThisMonth'] = 0
				else:
					categoryData['spentThisMonth'] = amount
				categoryData['transactions'] = transactions.values()
				
				for transaction in categoryData['transactions']:
					transaction['merchant'] = Merchant.objects.get(merchant_id=transaction['merchant_id']).merchant_name
					transaction['pymt_method_full'] = pymt[transaction['pymt_method']]
				
				rsp[c] = categoryData
			except:
				rsp[c] = categoryData
				print("idk")
				sys.stdout.flush()

		
		return Response(rsp, status=status.HTTP_200_OK)