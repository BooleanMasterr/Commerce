from django import forms
from .models import Comment, Listing


class Base(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'{field_name[0].upper()}{field_name[1:]}'


class CreateListingForm(Base):

    def __init__(self, *args, **kwargs):
        super(CreateListingForm, self).__init__(*args, **kwargs)
        self.fields['image_url'].widget.attrs['placeholder'] = 'Image Url (Optional)'

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'bid',
            'category',
            'image_url'
        ]


class CommentUpdateForm(Base):

    class Meta:
        model = Comment
        fields = [
            'content'
        ]


class CloseBiddingForm(Base):

    class Meta:
        model = Listing
        fields = [
            'is_closed'
        ]