from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models

from .constants import GENDER_CHOICE
from .managers import UserManager

from django.utils import timezone

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def balance(self):
        if hasattr(self, 'account'):
            return self.account.balance
        return 0
    otp = models.CharField(max_length=6, blank=True, null=True)  # Or the appropriate length for your OTP
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        import random
        self.otp = str(random.randint(100000, 999999))  # Generate a random 6-digit OTP
        self.otp_created_at = timezone.now()  # Set the current time
        self.save()

    def is_otp_valid(self, entered_otp):
        if self.otp == entered_otp and (timezone.now() - self.otp_created_at).seconds < 300:  # Valid for 5 minutes
            return True
        return False

    def clear_otp(self):
        self.otp = None
        self.otp_created_at = None
        self.save()




class UserBankAccount(models.Model):
    user = models.OneToOneField(
        User,
        related_name='account',
        on_delete=models.CASCADE,
    )
   
    account_no = models.PositiveIntegerField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birth_date = models.DateField(null=True, blank=True)
    balance = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2
    )
    interest_start_date = models.DateField(
        null=True, blank=True,
        help_text=(
            'The month number that interest calculation will start from'
        )
    )
    initial_deposit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.account_no)

    def get_interest_calculation_months(self):
        """
        List of month numbers for which the interest will be calculated

        returns [2, 4, 6, 8, 10, 12] for every 2 months interval
        """
        interval = int(
            12 / self.account_type.interest_calculation_per_year
        )
        start = self.interest_start_date.month
        return [i for i in range(start, 13, interval)]


class UserAddress(models.Model):
    user = models.OneToOneField(
        User,
        related_name='address',
        on_delete=models.CASCADE,
    )
    street_address = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    postal_code = models.PositiveIntegerField()
    country = models.CharField(max_length=256)

    def __str__(self):
        return self.user.email


from django.conf import settings

class Account(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_account'  # Ensure this is unique
    )
    account_number = models.CharField(max_length=20, unique=True)  # Ensure account numbers are unique
    
    # Add additional fields as necessary

    def __str__(self):
        return f"{self.user.email}'s Account"
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    # Add any additional fields you want for your custom user model
    # Example:
    phone_number = models.CharField(max_length=15, blank=True)

    # Override the groups and user_permissions fields
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'Notification for {self.user} - {self.message}'
    def mark_as_read(self):
        self.is_read = True
        self.save()
