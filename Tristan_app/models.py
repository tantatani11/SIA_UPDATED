from django.db import models

# Create your models here.
class Pet(models.Model):
    pet_id = models.IntegerField(primary_key=True)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    adoption_status = models.CharField(max_length=20)
    owner_name = models.CharField(max_length=100)

    def __str__(self):
        return self.pet_name