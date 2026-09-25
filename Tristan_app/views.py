from django.shortcuts import render
from .models import Pet

def pet(request):
    pet = Pet.objects.all()

    context = {
        'pet': pet
    }

    return render(request, 'PetApp/pet_management.html', context)
