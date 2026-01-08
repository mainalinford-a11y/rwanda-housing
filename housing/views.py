from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PropertyForm, AgentRatingForm, UserProfileForm, ChatForm
from .models import Property, PropertyImage, AgentRating, ChatMessage
from django.db.models import Avg, Q
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, filters
from .models import Property, ChatMessage
from .serializers import PropertySerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()

class IndexView(TemplateView):
    template_name = 'housing/index.html'

def buy_properties(request):
    properties = Property.objects.filter(listing_type='sale')
    return render(request, 'housing/buy.html', {'properties': properties})

def rent_properties(request):
    properties = Property.objects.filter(listing_type='rent')
    return render(request, 'housing/rent.html', {'properties': properties})

def agent_list(request):
    agents = User.objects.filter(user_type='agent').annotate(
        avg_rating=Avg('received_ratings__score')
    ).order_by('-avg_rating')
    return render(request, 'housing/agents.html', {'agents': agents})

@login_required
def rate_agent(request, agent_id):
    agent = get_object_or_404(User, id=agent_id, user_type='agent')
    
    if request.method == 'POST':
        form = AgentRatingForm(request.POST)
        if form.is_valid():
            rating, created = AgentRating.objects.update_or_create(
                agent=agent,
                rater=request.user,
                defaults={
                    'score': form.cleaned_data['score'],
                    'comment': form.cleaned_data['comment']
                }
            )
            messages.success(request, f'Thank you for rating {agent.get_full_name() or agent.username}!')
            return redirect('agent_list')
    
    return redirect('agent_list')

def sell_landing(request):
    return render(request, 'housing/sell.html')

def tools_landing(request):
    return render(request, 'housing/tools.html')

def register_view(request):
    if request.method == 'POST':
        # Simple manual validation for speed, ideal world use forms.py
        data = request.POST
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'housing/register.html', {'error': 'Passwords do not match'})
        
        try:
            user = User.objects.create_user(
                username=data.get('email'), # Using email as username
                email=data.get('email'),
                password=password,
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                user_type=data.get('user_type', 'buyer'),
                phone=data.get('phone'),
                is_active=False # Deactivate account until it is confirmed
            )
            
            # Send verification email
            current_site = get_current_site(request)
            subject = 'Activate Your Rwanda Housing Account'
            message = render_to_string('housing/emails/verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, 'no-reply@rwandahousing.com', [user.email])
            
            return render(request, 'housing/verification_sent.html')
        except IntegrityError:
            messages.error(request, 'An account with this email already exists. Please log in.')
            return redirect('login')
        except Exception as e:
            return render(request, 'housing/register.html', {'error': str(e)})
            
    return render(request, 'housing/register.html')

def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'housing/activation_success.html')
    else:
        return render(request, 'housing/activation_invalid.html')

def login_view(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            # Check if user exists but is inactive
            user_exists = User.objects.filter(username=username).first()
            if user_exists and not user_exists.is_active:
                # Re-verify password to be secure, otherwise people can probe for emails
                if user_exists.check_password(password):
                    return render(request, 'housing/login.html', {'error': 'Please check your email to activate your account before logging in.'})
            
            return render(request, 'housing/login.html', {'error': 'Invalid email or password'})
            
    return render(request, 'housing/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def add_property(request):
    if request.user.user_type not in ['seller', 'agent']:
        # Ideally show a permission denied page, but for now redirect with error or just home
        return render(request, 'housing/index.html', {'error': 'You must be a Seller or Agent to add properties.'})

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        files = request.FILES.getlist('images')
        
        if form.is_valid():
            if len(files) > 15:
                # Add error to form (non-field error or special)
                form.add_error(None, 'You can upload a maximum of 15 images.')
                return render(request, 'housing/add_property.html', {'form': form})
                
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            
            # Save images
            from .models import PropertyImage
            for f in files:
                PropertyImage.objects.create(property=property, image=f)
                
            return redirect('property_detail', pk=property.id) # Redirect to detail page to set thumbnail
    else:
        form = PropertyForm()
    
    return render(request, 'housing/add_property.html', {'form': form})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'housing/property_detail.html', {'property': property})

@login_required
def set_thumbnail(request, image_id):
    image = get_object_or_404(PropertyImage, pk=image_id)
    
    # Check ownership
    if image.property.owner != request.user:
        return redirect('index') # Or show permission error
        
    # Unset other thumbnails for this property
    PropertyImage.objects.filter(property=image.property).update(is_thumbnail=False)
    
    # Set this one
    image.is_thumbnail = True
    image.save()
    
    return redirect('property_detail', pk=image.property.id)

@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    
    if property.owner != request.user:
        return redirect('index')
        
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        files = request.FILES.getlist('images')
        
        if form.is_valid():
            current_image_count = property.images.count()
            if current_image_count + len(files) > 15:
                form.add_error(None, f'You can upload a maximum of 15 images. You currently have {current_image_count} and are trying to add {len(files)}.')
                return render(request, 'housing/edit_property.html', {'form': form, 'property': property})
                
            form.save()
            
            # Save new images
            for f in files:
                PropertyImage.objects.create(property=property, image=f)
                
            return redirect('property_detail', pk=property.id)
    else:
        form = PropertyForm(instance=property)
        
    return render(request, 'housing/edit_property.html', {'form': form, 'property': property})

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(PropertyImage, pk=image_id)
    property_id = image.property.id
    
    if image.property.owner != request.user:
        return redirect('index')
        
    image.delete()
    return redirect('edit_property', pk=property_id)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by('-created_at')
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['location', 'title', 'property_type', 'description']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Allow registration
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('agent_profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'housing/edit_profile.html', {'form': form})

def agent_profile(request, username):
    agent = get_object_or_404(User, username=username)
    # Annotate with avg rating
    agent_annotated = User.objects.filter(pk=agent.pk).annotate(
        avg_rating=Avg('received_ratings__score')
    ).first()
    properties = Property.objects.filter(owner=agent)
    return render(request, 'housing/agent_profile.html', {
        'agent': agent_annotated or agent,
        'properties': properties
    })

@login_required
def chat_view(request, username):
    receiver = get_object_or_404(User, username=username)
    if receiver == request.user:
        return redirect('inbox')
    
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=form.cleaned_data['message']
            )
            return redirect('chat_view', username=username)
    else:
        form = ChatForm()
    
    messages_list = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    ChatMessage.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'housing/chat.html', {
        'receiver': receiver,
        'messages_list': messages_list,
        'form': form
    })

@login_required
def inbox(request):
    # Get all users the current user has chatted with
    sent_to = ChatMessage.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = ChatMessage.objects.filter(receiver=request.user).values_list('sender', flat=True)
    
    chat_user_ids = set(list(sent_to) + list(received_from))
    chat_users = User.objects.filter(id__in=chat_user_ids)
    
    conversations = []
    for user in chat_users:
        last_message = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=request.user))
        ).last()
        unread_count = ChatMessage.objects.filter(sender=user, receiver=request.user, is_read=False).count()
        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort by last message timestamp
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else 0, reverse=True)
    
    return render(request, 'housing/inbox.html', {'conversations': conversations})
