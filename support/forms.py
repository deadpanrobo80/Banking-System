# forms.py
from django import forms
from .models import SupportTicket

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']

# forms.py
from django import forms
from .models import SupportTicket

class AdminResponseForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['response']  # Make sure 'response' is in the model
        widgets = {
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your response',
                'required': 'required',
                'rows': 4,
            }),
        }
