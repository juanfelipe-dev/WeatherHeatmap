"""
Forms for weather application.
"""

from django import forms
from .models import Location, WeatherAlert


class LocationForm(forms.ModelForm):
    """Form for creating and editing locations."""
    
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude', 'city', 'country', 'timezone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'required': True}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., UTC, America/New_York'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if latitude is not None:
            if not -90 <= latitude <= 90:
                self.add_error('latitude', 'Latitude must be between -90 and 90')
        
        if longitude is not None:
            if not -180 <= longitude <= 180:
                self.add_error('longitude', 'Longitude must be between -180 and 180')
        
        return cleaned_data


class WeatherAlertForm(forms.ModelForm):
    """Form for creating and editing weather alerts."""
    
    class Meta:
        model = WeatherAlert
        fields = ['location', 'alert_type', 'severity', 'description', 'start_time', 'end_time', 'is_active']
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'alert_type': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'End time must be after start time')
        
        return cleaned_data


class LocationBulkImportForm(forms.Form):
    """Form for bulk importing locations."""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='CSV format: name,latitude,longitude,city,country,timezone'
    )
