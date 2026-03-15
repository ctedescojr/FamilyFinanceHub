from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import BankAccount, Card, Category, Income, Expense, Wallet

@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display = ("user", "balance")
    readonly_fields = ("balance",) # As per user's business rule
    search_fields = ("user__username", "user__first_name", "user__last_name")

class CardInline(admin.TabularInline):
    model = Card
    extra = 1

@admin.register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ("user", "bank_name", "account_type", "balance")
    list_filter = ("account_type", "user")
    search_fields = ("bank_name", "user__username")
    readonly_fields = ("balance",) # As per user's business rule
    inlines = [CardInline]

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "user", "transaction_type")
    list_filter = ("transaction_type", "user")
    search_fields = ("name", "user__username")

@admin.register(Income)
class IncomeAdmin(ModelAdmin):
    list_display = ("description", "amount", "date", "user", "bank_account", "category")
    list_filter = ("date", "user", "category", "bank_account")
    search_fields = ("description", "user__username", "bank_account__bank_name")

@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ("description", "amount", "date", "user", "payment_method", "category")
    list_filter = ("date", "user", "payment_method", "category")
    search_fields = ("description", "place", "user__username")

