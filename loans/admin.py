from django.contrib import admin
from django.contrib import messages
from .models import Loan

class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'account', 'user', 'amount', 'status', 'remaining_balance', 'created_at', 'is_fully_repaid')  # Display account and user info
    list_filter = ('status', 'created_at', 'account__user')  # Allow filtering by user
    actions = ['approve_loans', 'reject_loans', 'mark_as_completed']

    def approve_loans(self, request, queryset):
        for loan in queryset:
            try:
                loan.approve_loan()  # Ensure this method exists in your Loan model
                loan.send_notification_email(
                    subject="Loan Approved",
                    message=f"Your loan of {loan.amount} has been approved. Please check your account for the updated balance.",
                    recipient_list=[loan.account.user.email]
                )
                self.message_user(request, f'Loan {loan.loan_id} approved successfully.', level=messages.SUCCESS)
            except ValueError as e:
                self.message_user(request, str(e), level=messages.ERROR)

    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        for loan in queryset:
            try:
                loan.reject_loan()  # Ensure this method exists in your Loan model
                loan.send_notification_email(
                    subject="Loan Rejected",
                    message=f"Your loan of {loan.amount} has been rejected. Please contact support for further assistance.",
                    recipient_list=[loan.account.user.email]
                )
                self.message_user(request, f'Loan {loan.loan_id} rejected successfully.', level=messages.SUCCESS)
            except ValueError as e:
                self.message_user(request, str(e), level=messages.ERROR)

    reject_loans.short_description = "Reject selected loans"

    def mark_as_completed(self, request, queryset):
        for loan in queryset:
            try:
                loan.status = 'completed'  # Update the status to 'completed'
                loan.remaining_balance = 0  # Optionally set remaining balance to zero
                loan.save()  # Save the loan object
                loan.send_notification_email(
                    subject="Loan Completed",
                    message=f"Your loan of {loan.amount} has been marked as completed.",
                    recipient_list=[loan.account.user.email]
                )
                self.message_user(request, f'Loan {loan.loan_id} marked as completed successfully.', level=messages.SUCCESS)
            except Exception as e:
                self.message_user(request, str(e), level=messages.ERROR)

    mark_as_completed.short_description = "Mark selected loans as completed"

    def user(self, obj):
        """Return the user associated with the loan."""
        return obj.account.user

    user.admin_order_field = 'account__user'  # Allows sorting by user
    user.short_description = 'User'  # Label for the column

admin.site.register(Loan, LoanAdmin)
