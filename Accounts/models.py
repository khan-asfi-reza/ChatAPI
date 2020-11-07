from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from Accounts.util import user_directory_path
from Accounts.manager import UserManager


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=128, editable=True, null=False, blank=False, unique=True)
    name = models.CharField(max_length=128, editable=True, null=False, blank=False)
    email = models.EmailField(editable=True, null=True, blank=True, unique=True)
    gender = models.PositiveSmallIntegerField(verbose_name='Gender', choices=[(1, 'Male'), (2, 'Female')],
                                              null=False, blank=False)
    # is the user active or not
    active = models.BooleanField(default=True)
    # a admin user; non super-user
    staff = models.BooleanField(default=False)
    # a superuser
    admin = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['gender', 'email', 'name']

    # calling user manager class
    objects = UserManager()

    def get_name(self):
        return self.name

    def __str__(self):
        return self.username

    @staticmethod
    def has_perm(perm, obj=None):
        # User permission to view
        return True

    @staticmethod
    def has_module_perms(app_label):
        # User permission to view
        return True

    @property
    def is_staff(self):
        # Returns true if user is staff
        return self.staff

    @property
    def is_superuser(self):
        return self.admin

    @property
    def is_admin(self):
        # returns true if user is admin or not
        return self.admin

    @property
    def is_active(self):
        # returns true if user is active or not
        return self.active

    @property
    def is_male(self):
        # returns true if user is active or not
        return self.gender == 1

    @property
    def is_female(self):
        # returns true if user is active or not
        return self.gender == 2


user_model = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(user_model, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=user_directory_path, default='user.png')
    online = models.BooleanField(default=False)
    last_online = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profile'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=user_model)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
