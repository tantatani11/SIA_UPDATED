from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AccountForm,
<<<<<<< HEAD
    AdoptionApplicationForm,
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    AnimalForm,
    EmailOrUsernameAuthenticationForm,
    ProfileForm,
    SignUpForm,
)
<<<<<<< HEAD
from .models import Pet, UserProfile, AdoptionApplication
=======
from .models import Pet, UserProfile
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f


class AnimalLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        return response


def _editable_animals(user):
    if user.is_staff:
        return Pet.objects.all()
    return Pet.objects.filter(owner=user)


def home(request):
    available_animals = Pet.objects.filter(
        adoption_status=Pet.STATUS_AVAILABLE,
    ).select_related('owner')
    return render(request, 'PetApp/home.html', {
        'available_count': available_animals.count(),
        'animal_count': Pet.objects.count(),
        'featured_animals': available_animals.order_by('-created_at')[:3],
    })


def directory(request):
    animals = Pet.objects.select_related('owner').all()
    query = request.GET.get('q', '').strip()
    species = request.GET.get('species', '').strip()
    breed = request.GET.get('breed', '').strip()
    location = request.GET.get('location', '').strip()
    status = request.GET.get('status', '').strip()
    sex = request.GET.get('sex', '').strip()
    age = request.GET.get('age', '').strip()

    if query:
        animals = animals.filter(
            Q(pet_name__icontains=query)
            | Q(species__icontains=query)
            | Q(breed__icontains=query)
        )
    if species:
        animals = animals.filter(species__icontains=species)
    if breed:
        animals = animals.filter(breed__icontains=breed)
    if location:
        animals = animals.filter(location__icontains=location)
    if status in {choice[0] for choice in Pet.STATUS_CHOICES}:
        animals = animals.filter(adoption_status=status)
    if sex in {choice[0] for choice in Pet.SEX_CHOICES}:
        animals = animals.filter(sex=sex)
    if age.isdigit():
        animals = animals.filter(age=int(age))

    sort = request.GET.get('sort', 'newest')
    sort_fields = {
        'oldest': 'created_at',
        'name': 'pet_name',
    }
    animals = animals.order_by(sort_fields.get(sort, '-created_at'), 'pet_id')
    page_obj = Paginator(animals, 12).get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'animals': page_obj.object_list,
        'filters': {
            'q': query,
            'species': species,
            'breed': breed,
            'location': location,
            'status': status,
            'sex': sex,
            'age': age,
            'sort': sort,
        },
        'species_list': Pet.objects.order_by('species').values_list('species', flat=True).distinct(),
        'status_choices': Pet.STATUS_CHOICES,
        'sex_choices': Pet.SEX_CHOICES,
    }
    return render(request, 'PetApp/directory.html', context)


@login_required
def dashboard(request):
    animals = Pet.objects.all()
    total = animals.count()
    available = animals.filter(adoption_status=Pet.STATUS_AVAILABLE).count()
    adopted = animals.filter(adoption_status=Pet.STATUS_ADOPTED).count()
    context = {
        'total_count': total,
        'available_count': available,
        'pending_count': animals.filter(adoption_status=Pet.STATUS_PENDING).count(),
        'adopted_count': adopted,
        'my_count': Pet.objects.filter(owner=request.user).count(),
        'recent_animals': animals.select_related('owner').order_by('-created_at')[:5],
        'updated_animals': animals.select_related('owner').order_by('-updated_at')[:5],
        'available_percent': round(available * 100 / total) if total else 0,
    }
    return render(request, 'PetApp/dashboard.html', context)


def animal_detail(request, pet_id):
    animal = get_object_or_404(Pet.objects.select_related('owner'), pk=pet_id)
<<<<<<< HEAD
    has_applied = False
    if request.user.is_authenticated:
        has_applied = AdoptionApplication.objects.filter(animal=animal, applicant=request.user).exists()
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    return render(request, 'PetApp/animal_detail.html', {
        'animal': animal,
        'can_manage': request.user.is_authenticated and (
            request.user.is_staff or animal.owner_id == request.user.pk
        ),
<<<<<<< HEAD
        'has_applied': has_applied,
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    })


@login_required
<<<<<<< HEAD
def adopt_apply(request, pet_id):
    animal = get_object_or_404(Pet, pk=pet_id)
    if animal.adoption_status == Pet.STATUS_ADOPTED:
        messages.error(request, 'This animal has already been adopted.')
        return redirect('animal_detail', pet_id=animal.pet_id)
    if AdoptionApplication.objects.filter(animal=animal, applicant=request.user).exists():
        messages.info(request, 'You have already submitted an application for this animal.')
        return redirect('animal_detail', pet_id=animal.pet_id)
    if request.user.is_staff or animal.owner_id == request.user.pk:
        messages.error(request, 'You cannot apply for your own listing.')
        return redirect('animal_detail', pet_id=animal.pet_id)

    form = AdoptionApplicationForm(request.POST or None, animal=animal, applicant=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your adoption application has been submitted.')
        return redirect('my_applications')
    return render(request, 'PetApp/adopt_apply.html', {'form': form, 'animal': animal})


@login_required
def my_applications(request):
    applications = AdoptionApplication.objects.filter(applicant=request.user).select_related('animal').order_by('-created_at')
    return render(request, 'PetApp/my_applications.html', {'applications': applications})


@login_required
@user_passes_test(lambda user: user.is_staff)
def manage_applications(request):
    applications = AdoptionApplication.objects.select_related('animal', 'applicant').order_by('-created_at')
    status_filter = request.GET.get('status', '').strip()
    if status_filter in {choice[0] for choice in AdoptionApplication.STATUS_CHOICES}:
        applications = applications.filter(status=status_filter)
    context = {
        'applications': applications,
        'status_choices': AdoptionApplication.STATUS_CHOICES,
        'status_filter': status_filter,
    }
    return render(request, 'PetApp/manage_applications.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_POST
def update_application_status(request, application_id):
    application = get_object_or_404(AdoptionApplication, pk=application_id)
    new_status = request.POST.get('status', '')
    notes = request.POST.get('notes', '').strip()
    if new_status in {choice[0] for choice in AdoptionApplication.STATUS_CHOICES}:
        application.status = new_status
        if notes:
            application.notes = notes
        application.save()
        if new_status == AdoptionApplication.STATUS_APPROVED:
            application.animal.adoption_status = Pet.STATUS_ADOPTED
            application.animal.save(update_fields=['adoption_status', 'updated_at'])
        messages.success(request, f'Application for {application.animal.pet_name} updated to {new_status}.')
    else:
        messages.error(request, 'Invalid status.')
    return redirect('manage_applications')


@login_required
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
def animal_create(request):
    form = AnimalForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        animal = form.save(commit=False)
        animal.owner = request.user
        if not animal.owner_name:
            animal.owner_name = request.user.get_full_name() or request.user.username
        animal.save()
        messages.success(request, 'Animal listing created.')
        return redirect('animal_detail', pet_id=animal.pk)
    return render(request, 'PetApp/animal_form.html', {'form': form, 'is_edit': False})


@login_required
def animal_update(request, pet_id):
    animal = get_object_or_404(_editable_animals(request.user), pk=pet_id)
    form = AnimalForm(request.POST or None, request.FILES or None, instance=animal)
    if request.method == 'POST' and form.is_valid():
        updated_animal = form.save(commit=False)
        if request.user.is_staff and updated_animal.owner_id is None:
            updated_animal.owner = request.user
        updated_animal.save()
        messages.success(request, 'Animal listing updated.')
        return redirect('animal_detail', pet_id=animal.pk)
    return render(request, 'PetApp/animal_form.html', {
        'form': form,
        'animal': animal,
        'is_edit': True,
    })


@require_POST
@login_required
def animal_delete(request, pet_id):
    animal = get_object_or_404(_editable_animals(request.user), pk=pet_id)
    animal.delete()
    messages.success(request, 'Animal listing removed.')
    return redirect('my_listings')


@login_required
def my_listings(request):
    animals = Pet.objects.filter(owner=request.user).select_related('owner').order_by('-updated_at')
    return render(request, 'PetApp/my_listings.html', {'animals': animals})


def sign_up(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            UserProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, 'Welcome! Your account is ready.')
        return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    account_form = AccountForm(request.POST or None, instance=request.user, prefix='account')
<<<<<<< HEAD
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, prefix='profile')
=======
    profile_form = ProfileForm(request.POST or None, instance=profile, prefix='profile')
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    if request.method == 'POST':
        if account_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                account_form.save()
                profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    return render(request, 'PetApp/profile.html', {
        'account_form': account_form,
        'profile_form': profile_form,
        'my_count': Pet.objects.filter(owner=request.user).count(),
<<<<<<< HEAD
        'profile_obj': profile,
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_dashboard(request):
    animals = Pet.objects.all()
    User = get_user_model()
    context = {
        'user_count': User.objects.count(),
        'animal_count': animals.count(),
        'available_count': animals.filter(adoption_status=Pet.STATUS_AVAILABLE).count(),
        'pending_count': animals.filter(adoption_status=Pet.STATUS_PENDING).count(),
        'adopted_count': animals.filter(adoption_status=Pet.STATUS_ADOPTED).count(),
        'recent_users': User.objects.order_by('-date_joined')[:6],
        'recent_animals': animals.select_related('owner').order_by('-updated_at')[:8],
    }
    return render(request, 'PetApp/admin_dashboard.html', context)
<<<<<<< HEAD


@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_manage_animals(request):
    animals = Pet.objects.select_related('owner').order_by('-updated_at')
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()
    if status_filter in {choice[0] for choice in Pet.STATUS_CHOICES}:
        animals = animals.filter(adoption_status=status_filter)
    if query:
        animals = animals.filter(
            Q(pet_name__icontains=query) | Q(species__icontains=query) | Q(owner__username__icontains=query)
        )
    return render(request, 'PetApp/admin_manage_animals.html', {
        'animals': animals,
        'status_choices': Pet.STATUS_CHOICES,
        'status_filter': status_filter,
        'query': query,
    })


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_POST
def admin_update_animal_status(request, pet_id):
    animal = get_object_or_404(Pet, pk=pet_id)
    new_status = request.POST.get('adoption_status', '')
    valid_statuses = {choice[0] for choice in Pet.STATUS_CHOICES}
    if new_status in valid_statuses:
        animal.adoption_status = new_status
        animal.save(update_fields=['adoption_status', 'updated_at'])
        messages.success(request, f'{animal.pet_name} status updated to {new_status}.')
    else:
        messages.error(request, 'Invalid status.')
    return redirect(request.META.get('HTTP_REFERER') or 'admin_manage_animals')
=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
