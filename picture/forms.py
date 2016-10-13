from django import forms
from picture.models import PaymentNote, Picture

class PaymentNoteForm(forms.ModelForm):
	class Meta:
		model = PaymentNote
		fields = ['message', 'name', 'number']

		widgets= {
			'message': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
			'number': forms.NumberInput(attrs={'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		self.picture = kwargs.pop('picture')
		return super().__init__(*args, **kwargs)

	def clean_number(self):

		data = self.cleaned_data['number']

		if not self.picture.has_at_least_n_left_uncovered(int(data)):
			raise forms.ValidationError("Not enough pixels are left to process that request")

		return data

