from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class AppUserManager(BaseUserManager):
	def create_user(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		email = self.normalize_email(email)
		user = self.model(email=email)
		user.set_password(password)
		user.save()
		return user
	def create_superuser(self, email, password=None):
		if not email:
			raise ValueError('An email is required.')
		if not password:
			raise ValueError('A password is required.')
		user = self.create_user(email, password)
		user.is_superuser = True
		user.save()
		return user

class AppUser(AbstractBaseUser, PermissionsMixin):
	user_id = models.AutoField(primary_key=True)
	email = models.EmailField(max_length=50, unique=True)
	username = models.CharField(max_length=50)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	objects = AppUserManager()
	def __str__(self):
		return self.username
	    
class Categories(models.Model): # Mapping table
    name = models.CharField(max_length=20, null=False, blank=False)
    abbr = models.CharField(max_length=2, null=False, blank=False)
    class Meta:
        managed = True
        db_table = "category"


class Merchant(models.Model):
    merchant_name = models.CharField(max_length=50, null=False, blank=False)
    category_id =  models.ForeignKey(Categories, on_delete=models.CASCADE, null=False, blank=False)
    class Meta:
        managed = True
        db_table = "merchant_xref"

class Transaction(models.Model):
    user_id = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=False, blank=False) # Remove entry when parent row is deleted (ie user)
    category_id = models.ForeignKey(Categories, on_delete=models.CASCADE, null=False, blank=False)
    merchant_id = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False)
    transaction_date = models.DateField(null=False, blank=False)
    pymt_method = models.CharField(max_length=2, blank=True)
    class Meta:
        managed = True
        db_table = "transaction"


class Budget(models.Model):
    user_id = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=False, blank=False) # Remove entry when parent row is deleted (ie user)
    frequency = models.CharField(max_length=10, null=False, blank=False)
    budget = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False)
    housing_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    utility_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    transportation_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    grocery_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    healthcare_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    dining_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    personal_care_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    entertainment_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    clothing_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    miscellaneous_lmt = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True) # any expenses that come up randomly
    status = models.CharField(max_length=2, null=False, blank=False)
    eff_from = models.DateTimeField(null=False, blank=False)
    eff_to = models.DateTimeField(null=False, blank=False)
    class Meta:
        managed = True
        db_table = "budget"


class Income(models.Model):
    user_id = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=False, blank=False)
    company = models.CharField(max_length=40, null=False, blank=False)
    income_dt = models.DateField(null=False, blank=False)
    class Meta:
        managed = True
        db_table = "income"

class TransactionCodes:
    HOUSING = 'HS'
    GROCERY = 'GC'
    ENTERTAINMENT = 'ET' 
    TRANSPORTATION = 'TP'
    TOILETRIES = 'TL'
    SUBSCRIPTION = 'SC'