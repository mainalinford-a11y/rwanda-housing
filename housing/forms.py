from django import forms
from .models import Property, AgentRating
from django.contrib.auth import get_user_model

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'listing_type', 'property_type', 'location', 'price', 'description'] # Removed 'image'
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'e.g. Modern Apartment in Kibagabaga'
            }),
            'listing_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
            }),
            'property_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
            }),
            'location': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'e.g. Kigali, Nyarutarama'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'placeholder': 'Enter amount in RWF'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'rows': 4,
                'placeholder': 'Describe the property features, amenities, nearby places...'
            }),
        }

class AgentRatingForm(forms.ModelForm):
    class Meta:
        model = AgentRating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'rows': 3,
                'placeholder': 'Explain your experience (optional)...'
            }),
        }
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'whatsapp', 'profile_picture', 'bio', 'locations', 'houses_sold', 'houses_rented']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'profile_picture': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'first_name': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'phone': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'whatsapp': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'locations': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm'}),
            'houses_sold': forms.NumberInput(attrs={'class': 'w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition'}),
            'houses_rented': forms.NumberInput(attrs={'class': 'w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition'}),
        }

class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 2,
        'class': 'block w-full px-4 py-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
        'placeholder': 'Type your message...'
    }))
