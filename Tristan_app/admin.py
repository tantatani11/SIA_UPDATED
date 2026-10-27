from django.contrib import admin
from .models import Pet, UserProfile


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
