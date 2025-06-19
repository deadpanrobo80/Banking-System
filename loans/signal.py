from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Loan

@receiver(post_save, sender=Loan)
def send_loan_notification(sender, instance, created, **kwargs):
    """Send email notifications after loan status change or repayment."""
    if not created:  # Only send when loan is updated, not created
        # Loan approval notification
        if instance.status == 'approved':
            instance.send_notification_email(
                subject='Loan Approved',
                message=f"Your {instance.category.name} loan of {instance.amount} has been approved at an interest rate of {instance.interest_rate}%.",
                recipient_list=[instance.account.user.email]
            )

        # Loan rejection notification
        elif instance.status == 'rejected':
            instance.send_notification_email(
                subject='Loan Rejected',
                message=f"Your {instance.category.name} loan of {instance.amount} has been rejected.",
                recipient_list=[instance.account.user.email]
            )

        # Loan completion notification
        elif instance.status == 'completed':
            instance.send_notification_email(
                subject='Loan Completed',
                message=f"Your {instance.category.name} loan of {instance.amount} has been marked as completed.",
                recipient_list=[instance.account.user.email]
            )
        
        # Repayment notification (only if remaining balance has decreased)
    if instance.remaining_balance < instance.amount and instance.status == "approved":  # Check if repayment occurred
            repayment_amount = instance.amount - instance.remaining_balance
            instance.send_notification_email(
                subject='Loan Repaid',
                message=f"Your {instance.category.name} loan of {instance.amount} has received a repayment of {repayment_amount}. Remaining balance: {instance.remaining_balance}.",
                recipient_list=[instance.account.user.email]
            )
