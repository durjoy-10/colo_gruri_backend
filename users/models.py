from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('guide', 'Guide'),
        ('traveller', 'Traveller'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='traveller')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be in format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    
    class Meta:
        db_table = 'users'
        verbose_name_plural = 'Users'