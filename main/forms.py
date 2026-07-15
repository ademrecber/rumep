from django import forms
from .models import RuxPdfComment

class RuxPdfCommentForm(forms.ModelForm):
    class Meta:
        model = RuxPdfComment
        fields = ['name', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adınız', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Yorumunuzu veya geri bildiriminizi buraya yazın...', 'rows': 4, 'required': True}),
        }
