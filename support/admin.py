# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from .models import SupportTicket
from .forms import AdminResponseForm

class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'message')

    actions = ['mark_as_closed', 'mark_as_in_review']

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, "Selected tickets have been marked as closed.")
    mark_as_closed.short_description = "Mark selected tickets as closed"

    def mark_as_in_review(self, request, queryset):
        queryset.update(status='in_review')
        self.message_user(request, "Selected tickets have been marked as in review.")
    mark_as_in_review.short_description = "Mark selected tickets as in review"

    def response_view(self, request, ticket_id):
        ticket = get_object_or_404(SupportTicket, pk=ticket_id)
        if request.method == 'POST':
            form = AdminResponseForm(request.POST, instance=ticket)
            if form.is_valid():
                ticket.response = form.cleaned_data['response']  # Save the admin's response
                ticket.status = 'closed'  # Mark ticket as closed
                ticket.save()  # Save the updated ticket
                self.message_user(request, "Response added successfully.")
                return redirect('..')  # Redirect back to the ticket list
        else:
            form = AdminResponseForm(instance=ticket)
        
        return render(request, 'supportticket_response.html', {'form': form, 'ticket': ticket})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('response/<int:ticket_id>/', self.admin_site.admin_view(self.response_view), name='ticket_response'),
        ]
        return custom_urls + urls

admin.site.register(SupportTicket, SupportTicketAdmin)
