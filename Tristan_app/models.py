from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from uuid import uuid4


def validate_animal_image(image):
    if image.size > 5 * 1024 * 1024:
        raise ValidationError('Choose an image smaller than 5 MB.')
    extension = image.name.rsplit('.', 1)[-1].lower() if '.' in image.name else ''
    image.seek(0)
    header = image.read(12)
    image.seek(0)
    valid_signatures = {
        'jpg': header.startswith(b'\xff\xd8\xff'),
        'jpeg': header.startswith(b'\xff\xd8\xff'),
        'png': header.startswith(b'\x89PNG\r\n\x1a\n'),
        'webp': header.startswith(b'RIFF') and header[8:12] == b'WEBP',
    }
    if not valid_signatures.get(extension, False):
        raise ValidationError('Upload a valid JPG, PNG, or WebP image.')


def animal_image_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1].lower()
    return f'animal_photos/{uuid4().hex}.{extension}'


class Pet(models.Model):
    STATUS_AVAILABLE = 'Available'
    STATUS_PENDING = 'Pending'
    STATUS_ADOPTED = 'Adopted'
    STATUS_LEGACY = 'Not Available'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_ADOPTED, 'Adopted'),
        (STATUS_LEGACY, 'Not Available (legacy)'),
    ]
    SEX_CHOICES = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Unknown', 'Unknown'),
    ]

    pet_id = models.AutoField(primary_key=True)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, db_index=True)
    breed = models.CharField(max_length=100)
    adoption_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE, db_index=True,
    )
    owner_name = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='animal_listings',
        null=True,
        blank=True,
    )
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True)
    description = models.TextField(blank=True)
    health_info = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True, db_index=True)
    image = models.FileField(
        upload_to=animal_image_path,
        blank=True,
        validators=[validate_animal_image],
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.pet_name

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.updated_at = timezone.now()
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'updated_at'}
        super().save(*args, **kwargs)


def profile_picture_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1].lower()
    from uuid import uuid4
    return f'profile_pics/{uuid4().hex}.{extension}'


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='animal_profile',
    )
    contact = models.CharField(max_length=40, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.FileField(
        upload_to=profile_picture_path,
        blank=True,
        validators=[validate_animal_image],
    )

    def __str__(self):
        return f'{self.user.username} profile'


class AdoptionApplication(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    application_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='adoption_applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adoption_applications',
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    address = models.TextField()
    household_info = models.TextField(help_text='Number of people, other pets, etc.')
    experience = models.TextField(help_text='Experience with this type of pet')
    reason = models.TextField(help_text='Why do you want to adopt this animal?')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('animal', 'applicant')

    def __str__(self):
        return f'Application for {self.animal.pet_name} by {self.applicant.username}'

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.updated_at = timezone.now()
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'updated_at'}
        super().save(*args, **kwargs)