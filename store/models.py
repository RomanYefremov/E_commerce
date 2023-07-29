from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True)  # New field for first name
    last_name = models.CharField(max_length=50, null=True)  # New field for last name
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)  # Added phone field
    city = models.CharField(max_length=100)  # New field for city
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else str(self.user.username)


@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)


class Size(models.Model):
    size_name = models.CharField(max_length=100)

    def __str__(self):
        return self.size_name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    is_available = models.BooleanField(default=True)
    quantity = models.IntegerField(default=0)  # Add the quantity field
    description = models.TextField(blank=True, null=True)
    material = models.TextField(blank=True, null=True)
    additional_material = models.TextField(blank=True, null=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=True, null=False)
    image = models.ImageField(null=True, blank=True)
    size_variant = models.ManyToManyField(Size, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def get_description(self):
        return self.description

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', blank=True)

    def __str__(self):
        return f"{self.product.name} Image"

class SizeVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size.size_name} - {self.quantity}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def remove_invalid_cart_items(self):
        order_items = self.orderitem_set.all()
        for order_item in order_items:
            if not order_item.product:
                order_item.delete()


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    size = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    @property
    def get_total(self):
        if self.product is None:
            return 0
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    phone_number = models.CharField(max_length=200, null=False)  # Added phone_number field
    email = models.EmailField(max_length=200, null=False)  # Added email field
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


class UserOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - Order {self.order.id}"


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Customer.objects.get_or_create(user=user, name=user.username, email=user.email)
        return user
