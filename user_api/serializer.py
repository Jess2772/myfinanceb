# convert complex model/data into simple python data types
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model, authenticate
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
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


class CategoryRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Categories
		fields = '__all__'
	def create(self, clean_data):
		category_obj = Categories.objects.create(name=clean_data['name'], abbr=clean_data['abbr'])
		return category_obj