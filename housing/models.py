from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('agent', 'Agent'),
        ('renter', 'Renter'),
        ('landlord', 'Landlord'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    houses_sold = models.IntegerField(default=0)
    houses_rented = models.IntegerField(default=0)
    locations = models.CharField(max_length=255, blank=True, null=True, help_text="Locations where the agent has properties")

    def __str__(self):
        return self.username

    def get_average_rating(self):
        ratings = self.received_ratings.all()
        if not ratings.exists():
            return 0
        return sum(r.score for r in ratings) / ratings.count()

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"

class AgentRating(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('agent', 'rater')

    def __str__(self):
        return f"{self.rater.username} rated {self.agent.username}: {self.score}"

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = (
        ('house', 'House'),
        ('flat', 'Flat'),
        ('apartment', 'Apartment'),
        ('bungalow', 'Bungalow'),
    )
    
    LISTING_TYPE_CHOICES = (
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    )
    
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='sale')
    description = models.TextField()
    image = models.ImageField(upload_to='properties/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_thumbnail(self):
        if self.images.filter(is_thumbnail=True).exists():
            return self.images.filter(is_thumbnail=True).first()
        elif self.images.exists():
            return self.images.first()
        elif self.image:
            return self
        return None

    class Meta:
        verbose_name_plural = "Properties"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    is_thumbnail = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.property.title}"
