import os
import django
from django.conf import settings
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_housing.settings')
django.setup()

from housing.models import Property, User

try:
    # Ensure we have a user and property
    user, created = User.objects.get_or_create(username='testuser', email='test@example.com')
    property, created = Property.objects.get_or_create(
        title='Test Property', 
        owner=user,
        description='Test Description',
        price=100000,
        location='Kigali'
    )

    print(f"Testing with Property ID: {property.id}")

    # Test Reverse
    try:
        url = reverse('edit_property', args=[property.id])
        print(f"Reverse success: {url}")
    except Exception as e:
        print(f"Reverse failed: {e}")

    # Test Template Rendering
    from housing.views import property_detail
    factory = RequestFactory()
    request = factory.get(f'/property/{property.id}/')
    request.user = user # Simulation logged in user

    try:
        response = property_detail(request, property.id)
        print("View execution success (status code):", response.status_code)
        # Force rendering
        if hasattr(response, 'render'):
             response.render()
        print("Template rendering success")
    except Exception as e:
        print(f"Template rendering failed: {e}")

except Exception as main_e:
    print(f"Setup failed: {main_e}")
