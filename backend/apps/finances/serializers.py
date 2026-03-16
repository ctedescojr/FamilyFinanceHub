from rest_framework import serializers
from .models import Wallet, BankAccount, Card, Category, Income, Expense

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for the user's wallet. The balance is read-only.
    """
    user = serializers.StringRelatedField()

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'updated_at']
        read_only_fields = ['balance']


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer for Card model.
    """
    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ('bank_account',) # The bank account is set on creation via nested route


class BankAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for BankAccount, with nested cards for read operations.
    """
    user = serializers.StringRelatedField()
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            'id', 'user', 'bank_name', 'account_type', 'balance', 
            'cards', 'created_at', 'updated_at'
        ]
        read_only_fields = ['balance', 'cards']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories, ensuring user cannot be changed.
    """
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('user',)


class IncomeSerializer(serializers.ModelSerializer):
    """
    Serializer for income transactions.
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Income
        fields = '__all__'

    def create(self, validated_data):
        # Associate the income with the logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for expense transactions.
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'

    def create(self, validated_data):
        # Associate the expense with the logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
