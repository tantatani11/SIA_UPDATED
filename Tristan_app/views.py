from django.shortcuts import render, redirect
from .models import Pet
from .forms import PetForm

def pet(request):
    pet = Pet.objects.all()

    if request.method == 'POST':
        form = PetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pet')

    else:
        form = PetForm()

    context = {
        'pet': pet,
        'form': form
    }

    return render(request, 'PetApp/pet_management.html', context)