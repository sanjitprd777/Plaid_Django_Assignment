from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plaid_django.settings import LOGIN_REDIRECT_URL
from .keys import *
from .models import Item


@login_required(login_url=LOGIN_REDIRECT_URL)
def index(request):
    keys = {
        'plaid_public_key': PLAID_PUBLIC_KEY,
        'plaid_environment': PLAID_ENV,
        'plaid_products': PLAID_PRODUCTS,
        'plaid_country_codes': PLAID_COUNTRY_CODES,

    }
    return render(request, "oauth.html", context=keys)


@login_required(login_url=LOGIN_REDIRECT_URL)
def home(request):
    items = Item.objects.filter(user=request.user)
    user = request.user
    transactions_query = items.values_list('account__transaction__name', "account__transaction__amount",
                                           'account__transaction__date').all()
    transactions = []
    cnt = 0
    for x in transactions_query:
        if cnt > 30:
            break
        if x[0]:
            x = {"name": x[0], "amount": x[1], "date": str(x[2])}
            transactions.append(x)
            cnt = cnt + 1
    if items.count() > 0:
        return render(request, 'home.html',
                      {'items': items, 'user': user, 'have_access_token': True, 'transactions': transactions})
    return render(request, 'home.html', {'user': user, 'have_access_token': False})


def loginview(request):
    return render(request, "login.html")


def signupview(request):
    return render(request, "signup.html")
