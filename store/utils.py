# import secrets
# import string
# from .models import TemporaryUser, Order
#
#
# def get_or_create_temporary_user(request):
#     unique_identifier = request.session.get('temporary_user_identifier')
#     if unique_identifier:
#         temporary_user, created = TemporaryUser.objects.get_or_create(unique_identifier=unique_identifier)
#     else:
#         # Generate a unique identifier and store it in the session.
#         unique_identifier = generate_unique_identifier()
#         request.session['temporary_user_identifier'] = unique_identifier
#         temporary_user, created = TemporaryUser.objects.get_or_create(unique_identifier=unique_identifier)
#
#     # Create or retrieve the order and associate it with the temporary user
#     order, _ = Order.objects.get_or_create(temporary_user=temporary_user, complete=False)
#
#     return temporary_user, order
#
#
# def generate_unique_identifier(length=12):
#     characters = string.ascii_letters + string.digits
#     identifier = ''.join(secrets.choice(characters) for _ in range(length))
#     return identifier
#
