# admin.py

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Product, Category, Customer, Order, OrderItem, ShippingAddress, SizeVariant, Size, ProductImage


class SizeVariantInline(admin.TabularInline):
    model = SizeVariant
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    # Add the image field to the form
    image = forms.ImageField(required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.image = self.cleaned_data.get('image')  # Set the image field from the form data
        if commit:
            instance.save()
        return instance


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'date_added', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="75" />', obj.image.url)
        else:
            return None

    display_image.short_description = 'Image'
    inlines = [SizeVariantInline, ProductImageInline]  # Include the ProductImageInline here


class SizeAdmin(admin.ModelAdmin):
    list_display = ['size_name']


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(SizeVariant)
admin.site.register(Size, SizeAdmin)
