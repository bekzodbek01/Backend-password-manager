from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    master_password = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Credential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credentials")
    service_name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    username = models.CharField(max_length=255)
    password = models.TextField()  # encrypted
    notes = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credentials"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service_name