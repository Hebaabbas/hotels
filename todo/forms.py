from django import forms
from django.contrib.auth.forms import UserCreationForm
from todo.models import CustomUser

# Custom form for user creation, inheriting from Django's UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'firstname', 'lastname', 'password1', 'password2')
    
    # Custom validation for the email field
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email.")
        return email
        
    # Overriding the save method to handle additional fields
    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.firstname = self.cleaned_data['firstname']
        user.lastname = self.cleaned_data['lastname']
        if commit:
            user.save()
        return user
