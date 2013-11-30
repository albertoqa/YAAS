from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class createAuction(forms.Form):
    title = forms.CharField()
    min_price = forms.FloatField()
    deadline = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], help_text="(Day/Month/Year Hour:Min)")
    description = forms.CharField(widget=forms.Textarea())


class confAuction(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    title = forms.CharField(widget=forms.HiddenInput())


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user