from django import forms
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):

    profile_image = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "profile_image"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("profile_image"):
            image = self.cleaned_data["profile_image"]
            user.profile_image = image.read()  
        if commit:
            user.save()
        return user