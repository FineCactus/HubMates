from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'venue', 'poster', 'college_name', 'organizer_email']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your event',
                'rows': 4,
                'required': True
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event venue/location',
                'required': True
            }),
            'poster': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'college_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'College/Institution name',
                'required': True
            }),
            'organizer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
                'required': True
            })
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            from django.utils import timezone
            if date < timezone.now().date():
                raise forms.ValidationError("Event date cannot be in the past.")
        return date
