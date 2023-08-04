from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Product, Category, Customer, Order, OrderItem, ShippingAddress, Variants, Size, ProductImage, Color


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class VariantsInline(admin.TabularInline):  # You can use admin.StackedInline if you prefer a stacked layout
    model = Variants
    extra = 1
    show_change_link = True


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.image = self.cleaned_data.get('image')
        if commit:
            instance.save()
        return instance


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer', 'product', 'quantity', 'variant', 'is_completed')
    list_filter = ('order',)

    def customer(self, obj):
        if obj.order is not None:
            return obj.order.customer  # Return the customer associated with the order
        return None  # Return None if the order is None

    customer.admin_order_field = 'order__customer'


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'get_orders', 'address', 'city', 'phone_number', 'email')
    list_filter = ('customer',)

    def get_orders(self, obj):
        orders = obj.customer.order_set.all()
        return ", ".join(str(order) for order in orders)

    get_orders.short_description = 'Orders'  # Set a custom header for the column




class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'date_added', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="75" />', obj.image.url)
        else:
            return None

    display_image.short_description = 'Image'
    inlines = [ProductImageInline, VariantsInline]  # Include the VariantsInline here


class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'color', 'size', 'price', 'quantity']


admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Variants, VariantsAdmin)
