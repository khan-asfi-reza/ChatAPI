from django import forms
from .models import User


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), label="Username",
                               required=True)
    name = forms.CharField(label='Name')
    email = forms.EmailField(label='Email Address')
    gender_choice = ((1, 'Male'), (2, 'Female'))
    gender = forms.RadioSelect(choices=gender_choice)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'gender')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email is taken")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is taken")
        return username

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}),
                               label="Username",
                               required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
                               required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username

    def clean_password(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        return password
