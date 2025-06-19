from django.db import models
from .constants import TRANSACTION_TYPE_CHOICES
from accounts.models import UserBankAccount
from accounts.models import Notification  # Assuming you have a Notification model

from .constants import TRANSACTION_TYPE_CHOICES, TRANSFER

class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount,
        related_name='transactions',
        on_delete=models.CASCADE,
    )
    sender_account = models.ForeignKey(
        UserBankAccount,
        related_name='sent_transactions',
        on_delete=models.CASCADE,
        null=True, blank=True  # Nullable for non-transfer transactions
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES  # Using the updated choices
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    reverted = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    def __str__(self):
        return f'Transaction {self.id} for Account {self.account.account_no} - Amount: {self.amount}'

    @classmethod
    def create_transfer(cls, sender_account, recipient_account, amount):
    # Ensure the sender has enough balance
     if sender_account.balance < amount:
        raise ValueError("Insufficient funds for transfer.")

    # Update balances before creating the transaction
     sender_account.balance -= amount
     recipient_account.balance += amount

    # Save updated balances
     sender_account.save()
     recipient_account.save()

    # Create the transaction and set both accounts
     return cls.objects.create(
        account=recipient_account,  # This is the recipient account
        sender_account=sender_account,  # This is the sender account
        amount=amount,
        balance_after_transaction=recipient_account.balance,
        transaction_type=TRANSFER  # Ensure this matches your constants
    )


    def revert_transaction(self):
        """
        Revert a flagged transaction and notify both users.
        """
        if self.reverted:
            raise ValueError("This transaction has already been reverted.")

        # Check if the transaction is a transfer
        if self.transaction_type != TRANSFER:
            raise ValueError("Reversal failed. This transaction is not a transfer.")

        # Get the recipient and sender accounts
        recipient_account = self.account
        sender_account = self.sender_account  # This should be populated
        
        if sender_account is None:
            raise ValueError("Reversal failed. No sender account available for this transaction.")

        # Adjust balances
        recipient_account.balance -= self.amount
        sender_account.balance += self.amount

        # Save the updated balances
        recipient_account.save()
        sender_account.save()

        # Mark the transaction as reverted
        self.reverted = True
        self.save()

        # Create a reversal transaction
        Transaction.objects.create(
            account=sender_account,
            sender_account=recipient_account,
            amount=self.amount,
            balance_after_transaction=sender_account.balance,
            transaction_type=TRANSFER  # Assuming you want to track it as a transfer
        )

        # Notify both users
        self.notify_users_about_reversion(sender_account, recipient_account)

    def notify_users_about_reversion(self, sender_account, recipient_account):
        # Notify the sender
        sender_notification_message = (
            f"A transfer of {self.amount} to {recipient_account.account_no} has been reversed. "
            f"Your balance is now {sender_account.balance}."
        )
        Notification.objects.create(
            user=sender_account.user,
            message=sender_notification_message
        )

        # Notify the recipient
        recipient_notification_message = (
            f"A transfer of {self.amount} from {sender_account.account_no} has been reversed. "
            f"Your balance is now {recipient_account.balance}."
        )
        Notification.objects.create(
            user=recipient_account.user,
            message=recipient_notification_message
        )


    def flag(self):
        self.flagged = True
        self.save()