from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, UserViewSet, IndexView, buy_properties, rent_properties, 
    agent_list, sell_landing, tools_landing, register_view, login_view, 
    logout_view, add_property, property_detail, set_thumbnail, edit_property, 
    delete_image, activate_view, rate_agent, agent_profile, edit_profile, 
    chat_view, inbox
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', IndexView.as_view(), name='index'),
    path('buy/', buy_properties, name='buy_properties'),
    path('rent/', rent_properties, name='rent_properties'),
    path('agents/', agent_list, name='agent_list'),
    path('sell/', sell_landing, name='sell_landing'),
    path('tools/', tools_landing, name='tools_landing'),
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate_view, name='activate'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add-property/', add_property, name='add_property'),
    path('property/<int:pk>/', property_detail, name='property_detail'),
    path('property/<int:pk>/edit/', edit_property, name='edit_property'),
    path('property/image/<int:image_id>/set-thumbnail/', set_thumbnail, name='set_thumbnail'),
    path('property/image/<int:image_id>/delete/', delete_image, name='delete_image'),
    path('rate-agent/<int:agent_id>/', rate_agent, name='rate_agent'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/@<str:username>/', agent_profile, name='agent_profile'),
    path('chat/@<str:username>/', chat_view, name='chat_view'),
    path('inbox/', inbox, name='inbox'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
