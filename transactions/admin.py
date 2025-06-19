from django.contrib import admin

from transactions.models import Transaction

from django.contrib import admin
from .models import Transaction
# admin.py

from django.contrib import admin
from .models import Transaction



# admin.py

from django.contrib import admin
from .models import Transaction

# admin.py

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id','account', 'amount', 'transaction_type', 'balance_after_transaction', 'timestamp', 'flagged', 'reverted')
    search_fields = ('account__account_no', 'transaction_type', 'amount')
    list_filter = ('transaction_type', 'timestamp', 'flagged', 'reverted')
    actions = ['mark_as_flagged', 'unmark_as_flagged', 'revert_transactions']

    def revert_transactions(self, request, queryset):
        """Revert selected transactions and notify users."""
        for transaction in queryset:
            try:
                transaction.revert_transaction()
            except ValueError as e:
                self.message_user(request, f"Error: {e}", level='error')
    
    revert_transactions.short_description = "Revert selected transactions"
    # admin.py
