import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda_housing.settings')
django.setup()

from django.contrib.auth import get_user_model
from housing.models import Property

User = get_user_model()

def run():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        print('Superuser created.')
    
    admin_user = User.objects.get(username='admin')
    
    if not Property.objects.exists():
        Property.objects.create(
            title="Luxury Villa in Kigali",
            location="Kigali, Nyarutarama",
            price=250000000,
            property_type="house",
            listing_type='sale',
            description="Beautiful 5 bedroom villa with pool.",
            owner=admin_user
        )
        print('Sample sale property created.')

    # Create Agent
    if not User.objects.filter(username='agent_john').exists():
        User.objects.create_user('agent_john', 'john@example.com', 'password123', first_name='John', last_name='Doe', user_type='agent')
        print('Agent user created.')
    
    # Create Rent Property
    if not Property.objects.filter(listing_type='rent').exists():
        Property.objects.create(
            title="Modern Apartment in Kacyiru",
            location="Kigali, Kacyiru",
            price=500000,
            property_type="apartment",
            listing_type='rent',
            description="2 bedroom apartment with city view.",
            owner=admin_user
        )
        print('Sample rent property created.')

if __name__ == '__main__':
    run()
