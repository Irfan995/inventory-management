from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime


# Create your models here.
class UserProfileManager(BaseUserManager):
    """
    Defines user creation fields and manages to save user
    """

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, username, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            password=password,
            username=username
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    """
    Creates a customized database table for user using customized user manager
    """

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    objects = UserProfileManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Product(models.Model):
    """
    Saves different unique products
    """
    product_name = models.CharField(max_length=256, null=True, blank=True)
    product_code = models.IntegerField(null=True, blank=True)
    category_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Child', 'Child')
    )
    category = models.CharField(max_length=128, choices=category_choices, null=True, blank=True)
    type = models.ForeignKey('ProductType', related_name='product', on_delete=models.CASCADE, null=True, blank=True)
    asset = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.product_name


class StockManagement(models.Model):
    """
    Stores product stock and manages sold quantity
    """
    product = models.ForeignKey('Product', related_name='stock_management', null=True, blank=True, on_delete=models.CASCADE)
    stock = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sold = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return 'Stock of {} : {}'.format(self.product.product_name, self.stock) 


class ProductType(models.Model):
    """
    Saves different product type
    """ 
    type_name = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self) -> str:
        return self.type_name


class ProductManagement(models.Model):
    """
    Store product unique barcode and manages product state
    """
    product = models.ForeignKey('Product', related_name='product_management', null=True, blank=True, on_delete=models.CASCADE)
    stock_keeping_unit = models.IntegerField(null=True, blank=True)
    bar_code = models.CharField(max_length=128, null=True, blank=True)
    status_choices = (
        ('Not Checked', 'Not Checked'),
        ('Damaged', 'Damaged'),
        ('Good', 'Good'),
        ('Sold', 'Sold')
    )
    product_state = models.CharField(
        max_length=128, choices=status_choices, null=True, blank=True, default='Not Checked')

    def __str__(self) -> str:
        return '{} | SKU: {}'.format(self.product.product_name, self.stock_keeping_unit)
    