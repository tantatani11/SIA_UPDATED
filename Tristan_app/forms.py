from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Pet, UserProfile, AdoptionApplication

User = get_user_model()


class AnimalForm(forms.ModelForm):
    SPECIES_CHOICES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Bird', 'Bird'),
        ('Fish', 'Fish'),
        ('Rabbit', 'Rabbit'),
        ('Hamster', 'Hamster'),
        ('Guinea pig', 'Guinea pig'),
        ('Turtle', 'Turtle'),
        ('Reptile', 'Reptile'),
        ('Ferret', 'Ferret'),
        ('Mouse', 'Mouse'),
        ('Rat', 'Rat'),
        ('Chinchilla', 'Chinchilla'),
        ('Hedgehog', 'Hedgehog'),
        ('Horse', 'Horse'),
        ('Other', 'Other (specify)'),
    ]
    species = forms.ChoiceField(
        choices=[('', 'Select species'), *SPECIES_CHOICES],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    species_other = forms.CharField(
        label='Specify species',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the animal species',
        }),
    )

    class Meta:
        model = Pet
        fields = [
            'pet_name', 'species', 'breed', 'age', 'sex', 'description',
            'health_info', 'adoption_status', 'location', 'owner_name', 'image',
        ]
        widgets = {
            'pet_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Animal name'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breed or mix'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': 'Age in years'}),
            'sex': forms.Select(attrs={'class': 'form-select'}, choices=[('', 'Select sex'), *Pet.SEX_CHOICES]),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Personality and what makes this animal special'}),
            'health_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Vaccination or health information (optional)'}),
            'adoption_status': forms.Select(attrs={'class': 'form-select'}, choices=Pet.STATUS_CHOICES[:3]),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or region'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact name'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        known_species = {value for value, _ in self.SPECIES_CHOICES if value != 'Other'}
        if self.instance.pk and self.instance.species not in known_species:
            self.initial['species'] = 'Other'
            self.initial['species_other'] = self.instance.species

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('species') == 'Other':
            species_other = cleaned_data.get('species_other', '').strip()
            if species_other:
                cleaned_data['species'] = species_other
            else:
                self.add_error('species_other', 'Enter the animal species.')
        return cleaned_data

class SignUpForm(UserCreationForm):
    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the terms and community guidelines.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or email',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'username'}),
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def clean(self):
        username = self.cleaned_data.get('username', '').strip()
        password = self.cleaned_data.get('password')
        if username and password:
            if '@' in username:
                matching_users = User.objects.filter(email__iexact=username)
                username = matching_users.first().get_username() if matching_users.count() == 1 else ''
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'contact', 'bio')
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone or other contact'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'maxlength': 500}),
        }


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ['full_name', 'email', 'phone', 'address', 'household_info', 'experience', 'reason']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'household_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Household details (people, pets, living situation)'}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Experience with this type of animal'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Why do you want to adopt this animal?'}),
        }

    def __init__(self, *args, **kwargs):
        self.animal = kwargs.pop('animal', None)
        self.applicant = kwargs.pop('applicant', None)
        super().__init__(*args, **kwargs)
        if self.applicant:
            if not self.initial.get('full_name'):
                self.initial['full_name'] = self.applicant.get_full_name() or self.applicant.username
            if not self.initial.get('email'):
                self.initial['email'] = self.applicant.email

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.animal:
            instance.animal = self.animal
        if self.applicant:
            instance.applicant = self.applicant
        if commit:
            instance.save()
        return instance
