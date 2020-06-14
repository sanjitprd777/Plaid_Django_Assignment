from django.urls import path
from . import views, views_api

urlpatterns = [
    path('link/', views.index, name="link"),
    path('home/', views.home, name="home"),
    path("signup/", views.signupview, name='signup'),
    path("login/", views.loginview, name='login'),

    # Below API calls use POST method
    path('api/signup/', views_api.UserCreate.as_view(), name='user-create'),
    path('api/login/', views_api.UserLogin.as_view(), name='user-login'),
    path('api/logout/', views_api.UserLogout.as_view(), name='user-logout'),
    path('api/get_access_token/', views_api.get_access_token.as_view(), name='get-access-token'),
    path('api/get_transactions/', views_api.get_transaction.as_view(), name='get-transaction'),

    # Below API calls use GET method
    path('api/identity/', views_api.get_identity.as_view(), name='get-identity'),
    path('api/balance/', views_api.get_balance.as_view(), name='get-balance'),
    path('api/item/', views_api.get_item_info.as_view(), name='get-item-info'),
    path('api/accounts/', views_api.get_balance.as_view(), name='get-balance'),
    path('api/webhook/', views_api.webhook, name='webhook'),
]
