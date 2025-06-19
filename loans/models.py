from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
from accounts.models import UserBankAccount

class LoanCategory(models.Model):
    """Represents loan categories like Personal, Home, etc."""
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.interest_rate}%"

class Loan(models.Model):
    """Represents a loan request made by the user."""
    LOAN_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    account = models.ForeignKey(
        UserBankAccount,
        related_name='loans',
        on_delete=models.CASCADE,
    )
    
    category = models.ForeignKey(
        LoanCategory,
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
   
    loan_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    repayment_start_date = models.DateTimeField(null=True, blank=True)
    repayment_period_months = models.PositiveIntegerField()
    remaining_balance = models.DecimalField(decimal_places=2, max_digits=12, default=0)

    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = uuid.uuid4()
        # Set interest rate from the category, if exists
        if self.category:
            self.interest_rate = self.category.interest_rate
        super().save(*args, **kwargs)
        self.send_notification_email(
            subject='Loan Application Sucessfully submitted ',
            message=f"Your {self.category.name} of {self.amount} has been submitted.Once decision has been made will let you. Thank you for choosing our services!",
            recipient_list=[self.account.user.email]
        )

    def __str__(self):
        return f"Loan {self.loan_id} - Amount: {self.amount} - Status: {self.status}"

    def approve_loan(self):
        """Approve the loan and send a notification email."""
        if self.status != 'pending':
            raise ValueError("Only pending loans can be approved.")

        self.status = 'approved'
        self.remaining_balance = self.amount
        self.repayment_start_date = timezone.now()
        self.save()
        self.account.balance += self.amount
        self.account.save()

        # Send loan approval notification
        self.send_notification_email(
            subject='Loan Approved',
            message=f"Your {self.category.name} loan of {self.amount} has been approved at an interest rateee of {self.interest_rate}%.",
            recipient_list=[self.account.user.email]
        )
    def repay_loan(self, repayment_amount):
        """Deduct repayment amount from the loan balance"""
        if self.status == 'approved' and self.remaining_balance > 0:
            self.remaining_balance -= repayment_amount
            self.save()

            # Deduct the repayment from the account's balance
            self.account.balance -= repayment_amount
            self.account.save()
            self.send_notification_email(
            subject='Loan Repaid',
            message=f"Your {self.category.name} loan of {self.amount} has been paid {self.repayment_amount}%.",
            recipient_list=[self.account.user.email]
        )

            # If loan is fully repaid, mark as completed
            if self.remaining_balance == 0:
                self.status = 'completed'
                self.save()

    def reject_loan(self):
        """Reject the loan and send a notification email."""
        if self.status != 'pending':
            raise ValueError("Only pending loans can be rejected.")

        self.status = 'rejected'
        self.save()

        # Send loan rejection notification
        self.send_notification_email(
            subject='Loan Rejected',
            message=f"Your {self.category.name} loan of {self.amount} has been rejected. Thank you for choosing our services!",
            recipient_list=[self.account.user.email]
        )

    def complete_loan(self):
        """Mark the loan as completed and send a notification email."""
        if self.status != 'approved':
            raise ValueError("Loan must be approved to be completed.")
        
        if self.remaining_balance > 0:
            raise ValueError("Loan cannot be completed until fully repaid.")
        
        self.status = 'completed'
        self.remaining_balance = 0
        self.save()

        # Send loan completion notification
        self.send_notification_email(
            subject='Loan Completed',
            message=f"Your {self.category.name} loan of {self.amount} has been marked as completed. Thank you!",
            recipient_list=[self.account.user.email]
        )
    def is_fully_repaid(self):
        """Check if the loan is fully repaid."""
        return self.remaining_balance == 0

    def send_notification_email(self, subject, message, recipient_list):
        """Utility function to send email notifications."""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Ensure you have a default email configured
            recipient_list,
            fail_silently=False,
        )
# loans/models.py
from django.db import models
from django.conf import settings  # Use settings.AUTH_USER_MODEL for user model reference

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans_notifications')  # added related_name
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
