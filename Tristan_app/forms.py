from .models import Pet
from django import forms

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ['pet_name', 'species', 'breed', 'adoption_status', 'owner_name']

        widgets = {
            'pet_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet name'}),
            'species': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet species'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet breed'}),
            'adoption_status': forms.Select(choices=[('Available', 'Available'),('Not Available', 'Not Available')],attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter owner name'}),
        }