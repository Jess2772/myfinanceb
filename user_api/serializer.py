# convert complex model/data into simple python data types
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
import datetime
from datetime import datetime
from django.utils import timezone
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, clean_data):
		user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
		user_obj.username = clean_data['username']
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField()
	##
	def check_user(self, clean_data):
		user = authenticate(username=clean_data['email'], password=clean_data['password'])
		if not user:
			raise ValidationError('user not found')
		return user

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ('email', 'username')


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class CategoryRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Categories
		fields = '__all__'
	
	def validate(self, data):
		category_name = data['category_name'].strip()

		if not category_name or Categories.objects.filter(category_name=category_name).exists():
			raise ValidationError('Category already exists.')
		
		return data
	
	def create(self, data):
		category_obj = Categories.objects.create(name=data['category_name'].strip(), last_modified=datetime.now(tz=timezone.utc))
		return category_obj
	
class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
	
class BudgetRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Budget
		fields = '__all__'

	def validate(self, data):
		frequency = data['frequency'].strip()
		budget = data['budget']
		housing_lmt = data['housing_lmt'] if 'housing_lmt' in data else None
		utility_lmt = data['utility_lmt'] if 'utility_lmt' in data else None
		transportation_lmt = data['transportation_lmt'] if 'transportation_lmt' in data else None
		grocery_lmt = data['grocery_lmt'] if 'grocery_lmt' in data else None
		healthcare_lmt = data['healthcare_lmt'] if 'healthcare_lmt' in data else None
		dining_lmt = data['dining_lmt'] if 'dining_lmt' in data else None
		entertainment_lmt = data['entertainment_lmt'] if 'entertainment_lmt' in data else None
		clothing_lmt = data['clothing_lmt'] if 'clothing_lmt' in data else None
		miscellaneous_lmt = data['miscellaneous_lmt'] if 'miscellaneous_lmt' in data else None

		if not frequency:
			raise ValidationError('Enter a frequency')
		
		if not budget or budget <= 0:
			raise ValidationError('Invalid budget amount')
		
		if housing_lmt and housing_lmt < 0:
			raise ValidationError('Invaild housing limit amount')

		if utility_lmt and utility_lmt < 0:
			raise ValidationError('Invalid utility limit amount')

		if transportation_lmt and transportation_lmt < 0:
			raise ValidationError('Invalid transportation limit amount')
		
		if grocery_lmt and grocery_lmt < 0:
			raise ValidationError('Invalid grocery limit amount')
		
		if healthcare_lmt and healthcare_lmt < 0:
			raise ValidationError('Invalid healthcare limit amount')

		if dining_lmt and dining_lmt < 0:
			raise ValidationError('Invalid dining limit amount')
		
		if entertainment_lmt and entertainment_lmt < 0:
			raise ValidationError('Invalid entertainment limit amount')

		if clothing_lmt and clothing_lmt < 0:
			raise ValidationError('Invalid clothing limit amount')

		if miscellaneous_lmt and miscellaneous_lmt < 0:
			raise ValidationError('Invalid miscellaneous limit amount')
		
		return data
	
	def create(self, data, user_id):
		budget_obj = Budget.objects.create(
			user_id = user_id,
			frequency = data['frequency'],
			budget = data['budget'],
			housing_lmt = data['housing_lmt'] if 'housing_lmt' in data else None,
			utility_lmt = data['utility_lmt'] if 'utility_lmt' in data else None,
			transportation_lmt = data['transportation_lmt'] if 'transportation_lmt' in data else None,
			grocery_lmt = data['grocery_lmt'] if 'grocery_lmt' in data else None,
			healthcare_lmt = data['healthcare_lmt'] if 'healthcare_lmt' in data else None,
			dining_lmt = data['dining_lmt'] if 'dining_lmt' in data else None,
			entertainment_lmt = data['entertainment_lmt'] if 'entertainment_lmt' in data else None,
			clothing_lmt = data['clothing_lmt'] if 'clothing_lmt' in data else None,
			miscellaneous_lmt = data['miscellaneous_lmt'] if 'miscellaneous_lmt' in data else None,
			is_active = "Y",
			eff_from = datetime.now(tz=timezone.utc),
			eff_to = datetime(9999, 12, 31, tzinfo=timezone.utc)
		)
		return budget_obj


class TransactionRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Transaction
		fields = ['amount', 'transaction_date', 'pymt_method']
	
	def validate(self, data):
		amount = data['amount']
		transaction_date = data['transaction_date']
		pymt_method = data['pymt_method'].strip()

		if not amount or amount <= 0:
			raise ValidationError("Invalid transaction amount")

		if not transaction_date:
			raise ValidationError("Transaction date not valid")
		
		if not pymt_method or len(pymt_method) != 2:
			raise ValidationError("Invalid payment method")
	
		return data

	def create(self, data, user_id, category_id, merchant_id):
		transaction_obj = Transaction.objects.create(
			user_id = user_id,
			category_id = category_id,
			merchant_id = merchant_id,
			amount = data['amount'],
			transaction_date = data['transaction_date'],
			pymt_method = data['pymt_method'] if 'pymt_method' in data else None
		)
		return transaction_obj
	

class MerchantRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Merchant
		fields = ['merchant_name']
	
	def validate(self, data):
		merchant_name = data['merchant_name'].strip()
		if not merchant_name:
			raise ValidationError("Not a valid merchant name")
		return data
		
	def create(self, data, category_id):
		merchant_obj = Merchant.objects.create(
			category_id = category_id,
			merchant_name = data['merchant_name'].strip(),
			last_modified=datetime.now(tz=timezone.utc)
		)
		return merchant_obj