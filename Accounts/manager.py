from django.contrib.auth.base_user import BaseUserManager

from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, username, name, gender, email, password):
        user = self.model.objects.filter(username=username, email=email)
        if self.model.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        elif self.model.objects.filter(email=email).exists():
            raise ValidationError('Email already used')
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.gender = gender
        user.name = name
        user.save(using=self._db)
        return user

    def create_staffuser(self, username, name, gender, email, password):
        # Creates a non super admin
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            gender=gender,
            name=name,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, gender, email, password):
        # Creates and saves a superuser with the given email and password.
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            gender=gender,
            name=name,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
