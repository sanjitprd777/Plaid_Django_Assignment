from __future__ import absolute_import, unicode_literals
from celery import shared_task
import datetime
import plaid
from .keys import *
from .models import Account, Item, Transaction


client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


@shared_task
def add(x, y):
    return x + y


@shared_task
def delete_transactions(item_id, removed_transactions):
    for transaction in removed_transactions:
        Transaction.objects.filter(transaction_id=transaction).delete()


@shared_task
def fetch_transactions(access_token=None, item_id=None, new_transactions=500):
    if access_token is None:
        access_token = Item.objects.filter(item_id=item_id)[0].access_token

    # transactions of two years i.e. 730 days
    start_date = '{:%Y-%m-%d}'.format(
        datetime.datetime.now() + datetime.timedelta(-730))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

    transactions_response = client.Transactions.get(
        access_token, start_date, end_date, {
            'count': new_transactions,
        })

    if item_id is None:
        item_id = transactions_response['item']['item_id']
    item = Item.objects.filter(item_id=item_id)[0]
    
    accounts = transactions_response['accounts']
    transactions = transactions_response['transactions']

    for account in accounts:
        account_list = Account.objects.filter(account_id=account['account_id'])
        if account_list.count() > 0:
            for a in account_list:
                a.balance_available = account['balances']['available']
                a.balance_current = account['balances']['current']
                a.save()

        else:
            account_obj = Account.objects.create(
                item=item,
                account_id=account['account_id'],
                balance_available=account['balances']['available'],
                balance_current=account['balances']['current'])

            account_obj.save()

    transaction_list = Transaction.objects.filter(
        account__item=item).order_by('-date')
    transaction_list_count = transaction_list.count()
    index = 0
    for transaction in transactions:
        if transaction_list_count > 0 and transaction['transaction_id'] == transaction_list[index].transaction_id:
            transaction_list[index].amount = transaction['amount']
            transaction_list[index].pending = transaction['pending']
            transaction_list[index].save()
            index += 1

        else:
            account_ = Account.objects.filter(
                account_id=transaction['account_id'])[0]

            transaction_obj = Transaction.objects.create(
                transaction_id=transaction['transaction_id'],
                account=account_,
                amount=transaction['amount'],
                date=transaction['date'],
                name=transaction['name'],
                pending=transaction['pending'])

            transaction_obj.save()
