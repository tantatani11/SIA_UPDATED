from django.contrib import admin
<<<<<<< HEAD
from .models import Pet, UserProfile, AdoptionApplication
=======
from .models import Pet, UserProfile
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('pet_name', 'species', 'breed', 'adoption_status', 'owner', 'location', 'updated_at')
    list_filter = ('adoption_status', 'species', 'sex')
    search_fields = ('pet_name', 'species', 'breed', 'owner_name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact')
    search_fields = ('user__username', 'user__email')
<<<<<<< HEAD


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'animal', 'applicant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('animal__pet_name', 'applicant__username', 'full_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
