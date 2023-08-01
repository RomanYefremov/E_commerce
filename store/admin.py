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
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Variants, VariantsAdmin)
