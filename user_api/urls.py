from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views
from .views import MyTokenObtainPairView

urlpatterns = [
    path('register', views.UserRegister.as_view(), name='register'),
	path('login', views.UserLogin.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name ='logout'),
	path('user', views.UserView.as_view(), name='user'),
    path('category', views.CategoryRegister.as_view(), name='category'),
    path('create/budget', views.BudgetRegister.as_view(), name='create_budget'),
    path('user/budget', views.UserBudget.as_view(), name='user_budget'),
    path('transaction', views.TransactionRegister.as_view(), name='transaction'),
    path('merchant', views.MerchantRegister.as_view(), name='merchant'),
    path('user/transaction', views.UserTransaction.as_view(), name ='add_transaction'),
    path('user/spending', views.UserSpending.as_view(), name ='spending'),
    path('user/spending/category', views.UserSpendingByCategory.as_view(), name ='spending_categories'),
    path('user/spending/month', views.UserMonthSpending.as_view(), name ='spending_month'),
    path('token/', 
          MyTokenObtainPairView.as_view(), 
          name ='token_obtain_pair'),
    path('token/refresh/', 
        jwt_views.TokenRefreshView.as_view(), 
        name ='token_refresh')
]
