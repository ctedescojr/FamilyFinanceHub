from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name=_("user"),
    )
    balance = models.DecimalField(
        _("balance"), max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.get_full_name()}'s Wallet"

    @transaction.atomic
    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.save(update_fields=["balance", "updated_at"])

    @transaction.atomic
    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save(update_fields=["balance", "updated_at"])
    
    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

class BankAccount(models.Model):
    class AccountType(models.TextChoices):
        CHECKING = "checking", _("Checking Account")
        SAVINGS = "savings", _("Savings Account")
        INVESTMENT = "investment", _("Investment")
        OTHER = "other", _("Other")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name=_("user"),
    )
    bank_name = models.CharField(_("bank name"), max_length=100)
    account_type = models.CharField(
        _("account type"),
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CHECKING,
    )
    balance = models.DecimalField(
        _("balance"), max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.bank_name} ({self.get_account_type_display()}) - {self.user.get_full_name()}"

    @transaction.atomic
    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.save(update_fields=["balance", "updated_at"])

    @transaction.atomic
    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save(update_fields=["balance", "updated_at"])

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        ordering = ["user", "bank_name"]


class Card(models.Model):
    class CardType(models.TextChoices):
        DEBIT = "debit", _("Debit")
        CREDIT = "credit", _("Credit")
        MULTIPLE = "multiple", _("Debit/Credit")

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("bank account"),
    )
    card_type = models.CharField(
        _("card type"),
        max_length=10,
        choices=CardType.choices,
        default=CardType.MULTIPLE,
    )
    name = models.CharField(_("card name"), max_length=100, help_text=_("e.g., Visa Platinum, Nubank Gold"))
    limit = models.DecimalField(
        _("limit"), max_digits=10, decimal_places=2, null=True, blank=True
    )
    statement_closing_day = models.PositiveSmallIntegerField(
        _("statement closing day"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    payment_due_day = models.PositiveSmallIntegerField(
        _("payment due day"),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self) -> None:
        is_debit = self.card_type == self.CardType.DEBIT
        has_credit_fields = any([
            self.limit is not None,
            self.statement_closing_day is not None,
            self.payment_due_day is not None,
        ])

        if is_debit and has_credit_fields:
            raise ValidationError(
                _("Debit cards cannot have a limit, statement closing day, or payment due day.")
            )

        is_credit = self.card_type in [self.CardType.CREDIT, self.CardType.MULTIPLE]
        if is_credit and self.limit is None:
            raise ValidationError(_("Credit cards must have a limit."))

    def __str__(self) -> str:
        return f"{self.name} ({self.get_card_type_display()})"

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")
        ordering = ["bank_account", "name"]


class Category(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("user"),
    )
    name = models.CharField(_("name"), max_length=100)
    transaction_type = models.CharField(
        _("transaction type"),
        max_length=10,
        choices=TransactionType.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_transaction_type_display()})"

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["user", "transaction_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "transaction_type"],
                name="unique_category_per_user",
            )
        ]


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name=_("user"),
    )
    description = models.CharField(_("description"), max_length=255)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    date = models.DateField(_("date"))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("category"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-date"]


class Income(Transaction):
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="incomes_registered",
        verbose_name=_("bank account"),
    )
    
    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            is_new = self.pk is None
            if is_new:
                self.bank_account.deposit(self.amount)
            else:
                original = type(self).objects.get(pk=self.pk)
                if original.bank_account.pk != self.bank_account.pk:
                    original.bank_account.withdraw(original.amount)
                    self.bank_account.deposit(self.amount)
                elif original.amount != self.amount:
                    difference = self.amount - original.amount
                    if difference > 0:
                        self.bank_account.deposit(difference)
                    else:
                        self.bank_account.withdraw(abs(difference))
            super().save(*args, **kwargs)

    class Meta(Transaction.Meta):
        verbose_name = _("Income")
        verbose_name_plural = _("Incomes")


class Expense(Transaction):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", _("Cash")
        PIX = "pix", _("PIX")
        DEBIT = "debit", _("Debit Card")
        CREDIT = "credit", _("Credit Card")

    place = models.CharField(_("place"), max_length=150, blank=True)
    payment_method = models.CharField(
        _("payment method"),
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses_pix",
        verbose_name=_("bank account (for PIX)"),
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses_card",
        verbose_name=_("card (for Debit/Credit)"),
    )

    def save(self, *args, **kwargs) -> None:
        with transaction.atomic():
            is_new = self.pk is None
            if not is_new:
                original = type(self).objects.get(pk=self.pk)
                # Revert original operation before applying the new one
                if original.payment_method == self.PaymentMethod.DEBIT and original.card:
                    original.card.bank_account.deposit(original.amount)
                elif original.payment_method == self.PaymentMethod.PIX and original.bank_account:
                    original.bank_account.deposit(original.amount)
                elif original.payment_method == self.PaymentMethod.CASH:
                    try:
                        original.user.wallet.deposit(original.amount)
                    except Wallet.DoesNotExist:
                        pass # Wallet might not exist, nothing to revert
            
            # Apply new operation
            if self.payment_method == self.PaymentMethod.DEBIT:
                self.card.bank_account.withdraw(self.amount)
            elif self.payment_method == self.PaymentMethod.PIX:
                self.bank_account.withdraw(self.amount)
            elif self.payment_method == self.PaymentMethod.CASH:
                try:
                    self.user.wallet.withdraw(self.amount)
                except Wallet.DoesNotExist:
                    raise ValidationError(_("User does not have a wallet to withdraw from."))

            super().save(*args, **kwargs)
            
    def clean(self) -> None:
        if self.payment_method == self.PaymentMethod.CASH:
            if self.bank_account or self.card:
                raise ValidationError(_("A card or bank account cannot be associated with a cash payment."))
        elif self.payment_method == self.PaymentMethod.PIX:
            if not self.bank_account or self.card:
                raise ValidationError(_("A bank account is required for PIX payments, and a card should not be selected."))
        elif self.payment_method in [self.PaymentMethod.DEBIT, self.PaymentMethod.CREDIT]:
            if not self.card or self.bank_account:
                raise ValidationError(_("A card is required for debit/credit payments, and a bank account should not be selected directly."))

    class Meta(Transaction.Meta):
        verbose_name = _("Expense")
        verbose_name_plural = _("Expenses")
