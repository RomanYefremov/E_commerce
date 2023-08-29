from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Category, Product, Order, OrderItem, ShippingAddress, Customer, Variants, Review
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm, ReviewForm
from django.db.models import Avg
import json
import datetime


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    categories = Category.objects.all()
    category = request.GET.get('category')
    if category is None:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(category__name=category)

    # Pagination
    paginator = Paginator(products, 15)  # 15 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cartItems': cartItems,
        'categories': categories
    }
    return render(request, 'store/store.html', context)


def product_detail(request, product_id):
    customer = None  # Initialize customer as None by default
    if request.user.is_authenticated:
        customer = request.user.customer

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    review_count = Review.objects.filter(product=product).count()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    average_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating) if average_rating else 0

    user_review = Review.objects.filter(product=product, user=request.user).first()
    other_reviews = Review.objects.filter(product=product).exclude(user=request.user).order_by('-created_at')
    user_has_review = user_review is not None
    # If the user has left a review, move it to the beginning of the list
    if user_review:
        reviews = [user_review] + list(other_reviews)
    else:
        reviews = list(other_reviews)

    cartItems = order.get_cart_items
    # sizes = SizeVariant.objects.all()
    context = {'product': product,
               'cartItems': cartItems,
               'reviews': reviews,
               'form': form,
               'review_count': review_count,
               'user_review': user_review,
               'average_rating': average_rating,
               }
    return render(request, 'store/product_detail.html', context)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product_detail', product_id=review.product.id)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_review(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id, user=request.user)
        review.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.remove_invalid_cart_items()  # Remove invalid cart items
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # Create empty cart for now for non-logged in user
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    try:
        data = json.loads(request.body)
        print('Received data:', data)
        variantId = data['variantId']
        action = data['action']
        print('Action:', action)
        print('Product Variant ID:', variantId)

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Get the product variant associated with the selected variantId
        variant = Variants.objects.get(id=variantId)

        # Check if the order item already exists for the selected variant
        order_item, created = OrderItem.objects.get_or_create(order=order, product=variant.product, variant=variant)

        if action == 'add':
            order_item.quantity += 1
        elif action == 'remove':
            order_item.quantity -= 1

        order_item.save()

        if order_item.quantity <= 0:
            order_item.delete()

        return JsonResponse({'message': 'Item was added'})
    except json.JSONDecodeError as e:
        print('Error decoding JSON:', str(e))
        return JsonResponse('Error decoding JSON', status=400, safe=False)
    except KeyError as e:
        print('KeyError:', str(e))
        return JsonResponse('Invalid data in request', status=400, safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        order_items = order.orderitem_set.all()
        for item in order_items:
            item.is_paid_and_ready = True
            item.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                city=data['shipping']['city'],
                address=data['shipping']['address'],
                phone_number=data['shipping']['phone_number'],
                email=data['shipping']['email'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)




def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()

            try:
                customer = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                customer = Customer(user=user)

            customer.email = email
            customer.first_name = form.cleaned_data['first_name']
            customer.last_name = form.cleaned_data['last_name']
            customer.save()

            user = authenticate(request, username=user.username, password=password)
            login(request, user)
            return redirect('store')
    else:
        form = RegistrationForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def personal_area(request):
    user = request.user
    orders = Order.objects.filter(customer=user.customer)

    order_items_with_status = []
    for order in orders:
        order_items = order.orderitem_set.all()
        for item in order_items:
            order_item_status = {
                'order_item': item,
                'is_paid_and_ready': item.is_paid_and_ready,  # Assuming you have this field
                'is_completed': item.is_completed,  # Assuming you have this field
                'variant': item.variant,  # Assuming you have this field
            }
            order_items_with_status.append(order_item_status)

    context = {
        'user': user,
        'order_items_with_status': order_items_with_status,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    return render(request, 'store/personal_area.html', context)


def save_field(request, field_name):
    if request.method == 'POST':
        value = request.POST.get(field_name)
        if value is not None:
            user = request.user
            customer = user.customer
            setattr(customer, field_name, value)
            customer.save()
    return redirect('personal_area')

def save_phone(request):
    return save_field(request, 'phone')

def save_address(request):
    return save_field(request, 'address')

def save_city(request):
    return save_field(request, 'city')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
    return render(request, 'store/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('store')
