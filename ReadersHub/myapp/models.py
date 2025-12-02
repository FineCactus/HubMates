from django.db import models
from django.utils import timezone

# Create your models here.

class Event(models.Model):
    # Event details
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default='09:00:00')
    venue = models.CharField(max_length=300, default='TBD')
    poster = models.ImageField(upload_to='event_posters/')
    college_name = models.CharField(max_length=200)
    
    # Organizer details
    organizer_email = models.EmailField()
    
    # System fields
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
