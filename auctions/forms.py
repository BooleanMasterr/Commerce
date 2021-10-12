from django import forms
from .models import Comment, Listing
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class Base(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs[
                "placeholder"
            ] = f"{field_name[0].upper()}{field_name[1:]}"


class CreateListingForm(Base):
    def __init__(self, *args, **kwargs):
        super(CreateListingForm, self).__init__(*args, **kwargs)
        self.fields["image_url"].widget.attrs["placeholder"] = "Image Url (Optional)"

    class Meta:
        model = Listing
        fields = ["title", "description", "bid", "category", "image_url"]


class CommentUpdateForm(Base):
    class Meta:
        model = Comment
        fields = ["content"]


class CloseBiddingForm(Base):
    class Meta:
        model = Listing
        fields = ["is_closed"]


class UserRegistrationForm(Base, UserCreationForm):

    email = forms.EmailField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, *kwargs)

        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]
