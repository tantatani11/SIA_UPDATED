from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Pet, UserProfile

User = get_user_model()


class DirectoryTests(TestCase):
    def setUp(self):
        self.animal = Pet.objects.create(
            pet_name='Milo',
            species='Dog',
            breed='Terrier',
            age=4,
            sex='Male',
            adoption_status=Pet.STATUS_AVAILABLE,
            location='Cebu',
            owner_name='Alex',
        )

    def test_directory_is_public_and_shows_animal(self):
        response = self.client.get(reverse('directory'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Milo')
        self.assertContains(response, 'Terrier')

<<<<<<< HEAD
    def test_view_details_opens_the_selected_animal(self):
        response = self.client.get(reverse('directory'))
        detail_url = reverse('animal_detail', args=[self.animal.pk])

        self.assertContains(response, f'href="{detail_url}" class="btn btn-outline-green btn-sm mt-3">View details</a>')

        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Milo')
        self.assertContains(detail_response, 'Terrier')

    def test_view_details_renders_listing_without_an_owner(self):
        legacy_animal = Pet.objects.create(
            pet_name='Legacy listing',
            species='Cat',
            breed='Domestic shorthair',
        )

        response = self.client.get(reverse('animal_detail', args=[legacy_animal.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Animal Adoption community')

=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    def test_directory_search_filters_name_species_and_breed(self):
        response = self.client.get(reverse('directory'), {'q': 'Terrier'})

        self.assertContains(response, 'Milo')
        self.assertEqual(len(response.context['animals']), 1)

        response = self.client.get(reverse('directory'), {'q': 'turtle'})
        self.assertNotContains(response, 'Milo')
        self.assertEqual(len(response.context['animals']), 0)

    def test_directory_applies_filters_and_sorting(self):
        Pet.objects.create(
            pet_name='Asha',
            species='Cat',
            breed='Tabby',
            age=2,
            sex='Female',
            adoption_status=Pet.STATUS_PENDING,
            location='Manila',
            owner_name='Sam',
        )

        response = self.client.get(reverse('directory'), {
            'species': 'Cat', 'status': Pet.STATUS_PENDING, 'sex': 'Female',
            'age': '2', 'location': 'Manila', 'sort': 'name',
        })

        self.assertEqual([animal.pet_name for animal in response.context['animals']], ['Asha'])

    def test_legacy_pet_management_url_redirects_to_directory(self):
        response = self.client.get(reverse('pet'))
        self.assertRedirects(response, reverse('directory'))

    def test_homepage_is_public_landing_page_with_live_information_and_featured_animals(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Every animal deserves a place to call home.')
        self.assertContains(response, 'About Animal Adoption')
        self.assertContains(response, 'Meet the animals')
        self.assertContains(response, 'Milo')
        self.assertEqual(response.context['animal_count'], 1)
        self.assertEqual(response.context['available_count'], 1)
        self.assertEqual(list(response.context['featured_animals']), [self.animal])


class AccountAndListingTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='StrongPass!934',
        )
        self.other_user = User.objects.create_user(
            username='visitor', email='visitor@example.com', password='StrongPass!934',
        )
        self.animal = Pet.objects.create(
            pet_name='Milo',
            species='Dog',
            breed='Terrier',
            adoption_status=Pet.STATUS_AVAILABLE,
            owner_name='Owner',
            owner=self.owner,
        )

    def test_signup_creates_user_profile_and_authenticates(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newperson',
            'first_name': 'New',
            'last_name': 'Person',
            'email': 'new@example.com',
            'password1': 'SafePass!847263',
            'password2': 'SafePass!847263',
            'terms_accepted': 'on',
        })

        self.assertRedirects(response, reverse('dashboard'))
        new_user = User.objects.get(username='newperson')
        self.assertTrue(new_user.check_password('SafePass!847263'))
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user.pk)

    def test_signup_rejects_duplicate_email_case_insensitively(self):
        response = self.client.post(reverse('signup'), {
            'username': 'duplicate',
            'first_name': 'New',
            'last_name': 'Person',
            'email': 'OWNER@example.com',
            'password1': 'SafePass!847263',
            'password2': 'SafePass!847263',
            'terms_accepted': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email already exists.')
        self.assertFalse(User.objects.filter(username='duplicate').exists())

    def test_login_accepts_email_and_logout_requires_post(self):
        response = self.client.post(reverse('login'), {
            'username': self.owner.email,
            'password': 'StrongPass!934',
            'remember_me': 'on',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.owner.pk)

        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_uses_live_adoption_counts_and_current_users_listings(self):
        Pet.objects.create(
            pet_name='Penny',
            species='Cat',
            breed='Tabby',
            adoption_status=Pet.STATUS_PENDING,
            owner_name='Owner',
            owner=self.owner,
        )
        Pet.objects.create(
            pet_name='Rex',
            species='Dog',
            breed='Mixed',
            adoption_status=Pet.STATUS_ADOPTED,
            owner_name='Visitor',
            owner=self.other_user,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['total_count'], 3)
        self.assertEqual(response.context['available_count'], 1)
        self.assertEqual(response.context['pending_count'], 1)
        self.assertEqual(response.context['adopted_count'], 1)
        self.assertEqual(response.context['my_count'], 2)

    def test_create_listing_requires_auth_and_sets_owner(self):
        create_url = reverse('animal_create')
        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('login')}?next={create_url}")

        self.client.force_login(self.owner)
        response = self.client.post(create_url, {
            'pet_name': 'Poppy',
            'species': 'Rabbit',
            'breed': 'Mini Lop',
            'age': 1,
            'sex': 'Female',
            'description': 'Gentle and curious.',
            'health_info': '',
            'adoption_status': Pet.STATUS_AVAILABLE,
            'location': 'Cebu',
            'owner_name': '',
        })
        new_animal = Pet.objects.get(pet_name='Poppy')
        self.assertRedirects(response, reverse('animal_detail', args=[new_animal.pk]))
        self.assertEqual(new_animal.owner, self.owner)
        self.assertEqual(new_animal.owner_name, 'owner')

<<<<<<< HEAD
    def test_create_listing_accepts_custom_species(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('animal_create'), {
            'pet_name': 'Pip',
            'species': 'Other',
            'species_other': 'Sugar glider',
            'breed': 'Standard grey',
            'adoption_status': Pet.STATUS_AVAILABLE,
            'owner_name': 'Owner',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Pet.objects.get(pet_name='Pip').species, 'Sugar glider')

    def test_editing_custom_species_keeps_existing_value(self):
        custom_animal = Pet.objects.create(
            pet_name='Pip',
            species='Sugar glider',
            breed='Standard grey',
            owner=self.owner,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('animal_update', args=[custom_animal.pk]))

        self.assertContains(response, '<option value="Other" selected>Other (specify)</option>', html=True)
        self.assertContains(response, 'value="Sugar glider"')

=======
>>>>>>> 4a51f2e52da787607f79032f8515351c80a6b59f
    def test_create_listing_rejects_non_image_upload(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('animal_create'), {
            'pet_name': 'Poppy',
            'species': 'Rabbit',
            'breed': 'Mini Lop',
            'adoption_status': Pet.STATUS_AVAILABLE,
            'owner_name': 'Owner',
            'image': SimpleUploadedFile('fake.jpg', b'not actually an image', content_type='image/jpeg'),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload a valid JPG, PNG, or WebP image.')
        self.assertFalse(Pet.objects.filter(pet_name='Poppy').exists())

    def test_owner_can_edit_and_delete_own_listing(self):
        self.client.force_login(self.owner)
        edit_url = reverse('animal_update', args=[self.animal.pk])
        response = self.client.post(edit_url, {
            'pet_name': 'Milo',
            'species': 'Dog',
            'breed': 'Mixed breed',
            'adoption_status': Pet.STATUS_ADOPTED,
            'owner_name': 'Owner',
        })
        self.assertRedirects(response, reverse('animal_detail', args=[self.animal.pk]))
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.breed, 'Mixed breed')
        self.assertEqual(self.animal.adoption_status, Pet.STATUS_ADOPTED)

        response = self.client.post(reverse('animal_delete', args=[self.animal.pk]))
        self.assertRedirects(response, reverse('my_listings'))
        self.assertFalse(Pet.objects.filter(pk=self.animal.pk).exists())

    def test_user_cannot_update_or_delete_another_users_listing(self):
        self.client.force_login(self.other_user)
        edit_url = reverse('animal_update', args=[self.animal.pk])
        delete_url = reverse('animal_delete', args=[self.animal.pk])

        self.assertEqual(self.client.get(edit_url).status_code, 404)
        self.assertEqual(self.client.post(edit_url, {
            'pet_name': 'Hijacked',
            'species': 'Dog',
            'breed': 'Terrier',
            'adoption_status': Pet.STATUS_ADOPTED,
            'owner_name': 'Visitor',
        }).status_code, 404)
        self.assertEqual(self.client.post(delete_url).status_code, 404)
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.pet_name, 'Milo')
        self.assertTrue(Pet.objects.filter(pk=self.animal.pk).exists())

    def test_legacy_unowned_listings_are_not_modifiable_by_regular_users(self):
        legacy = Pet.objects.create(
            pet_name='Legacy',
            species='Bird',
            breed='Finch',
            adoption_status=Pet.STATUS_LEGACY,
        )
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(reverse('animal_update', args=[legacy.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('animal_delete', args=[legacy.pk])).status_code, 404)

    def test_my_listings_only_shows_the_signed_in_users_records(self):
        other_animal = Pet.objects.create(
            pet_name='Visitor animal',
            species='Bird',
            breed='Finch',
            adoption_status=Pet.STATUS_AVAILABLE,
            owner_name='Visitor',
            owner=self.other_user,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('my_listings'))

        self.assertContains(response, 'Milo')
        self.assertNotContains(response, other_animal.pet_name)
        self.assertEqual(list(response.context['animals']), [self.animal])

    def test_staff_can_manage_any_listing_and_view_admin_panel(self):
        staff_user = User.objects.create_user(
            username='moderator', email='staff@example.com', password='StrongPass!934', is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin panel')
        self.assertEqual(self.client.get(reverse('animal_update', args=[self.animal.pk])).status_code, 200)
        self.assertEqual(self.client.post(reverse('animal_delete', args=[self.animal.pk])).status_code, 302)

    def test_regular_user_cannot_view_admin_panel(self):
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(reverse('admin_dashboard')).status_code, 302)

    def test_profile_update_only_changes_signed_in_user(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('profile'), {
            'account-first_name': 'Updated',
            'account-last_name': 'Owner',
            'account-email': 'new-owner@example.com',
            'profile-contact': '555-0123',
            'profile-bio': 'I foster animals.',
        })

        self.assertRedirects(response, reverse('profile'))
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.email, 'new-owner@example.com')
        self.assertEqual(self.owner.animal_profile.contact, '555-0123')
        self.assertEqual(self.owner.animal_profile.bio, 'I foster animals.')
        self.assertEqual(self.other_user.email, 'visitor@example.com')

    def test_animal_status_and_profile_are_not_publicly_editable(self):
        response = self.client.get(reverse('animal_detail', args=[self.animal.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit listing')
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)

    def test_password_change_uses_django_password_validation(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('password_change'), {
            'old_password': 'StrongPass!934',
            'new_password1': 'NewStrongPass!435',
            'new_password2': 'NewStrongPass!435',
        })

        self.assertRedirects(response, reverse('password_change_done'))
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('NewStrongPass!435'))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_flow_sends_reset_email(self):
        response = self.client.post(reverse('password_reset'), {'email': self.owner.email})

        self.assertRedirects(response, reverse('password_reset_done'))
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('accounts/reset/', mail.outbox[0].body)

    def test_regular_account_does_not_get_admin_access_from_profile_submission(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('profile'), {
            'account-first_name': 'Owner',
            'account-last_name': '',
            'account-email': self.owner.email,
            'profile-contact': '',
            'profile-bio': '',
            'is_staff': 'on',
            'is_superuser': 'on',
        })
        self.owner.refresh_from_db()
        self.assertFalse(self.owner.is_staff)
        self.assertFalse(self.owner.is_superuser)
