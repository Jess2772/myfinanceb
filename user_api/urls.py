from django.urls import path
from . import views

urlpatterns = [
    path('register', views.UserRegister.as_view(), name='register'),
	path('login', views.UserLogin.as_view(), name='login'),
	path('logout', views.UserLogout.as_view(), name='logout'),
	path('user', views.UserView.as_view(), name='user'),
    path('category', views.CategoryRegister.as_view(), name='category'),
    path('budget', views.BudgetRegister.as_view(), name='budget'),
    path('transaction', views.TransactionRegister.as_view(), name='transaction'),
    path('merchant', views.MerchantRegister.as_view(), name='merchant'),
]
