from django.contrib import admin
from .models import Account, Item, Transaction


class AccountEntry(admin.ModelAdmin):
    list_display = ("id", "account_id", "item",
                    "balance_available", "balance_current")


class ItemEntry(admin.ModelAdmin):
    list_display = ("id", "item_id", "access_token", "user")


class TransactionEntry(admin.ModelAdmin):
    list_display = ("id", "transaction_id", "account",
                    "amount", "date", "name", "pending")


admin.site.register(Account, AccountEntry)
admin.site.register(Item, ItemEntry)
admin.site.register(Transaction, TransactionEntry)
