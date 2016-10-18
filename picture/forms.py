from django import forms
from picture.models import PaymentNote, Picture

NUMBER_PRESET_OPTIONS = (
	(5, '5'),
	(10, '10'),
	(20, '20'),
	(0, 'Custom')
)

class PaymentNoteForm(forms.ModelForm):
	number_preset = forms.ChoiceField(required=False, choices=NUMBER_PRESET_OPTIONS, widget=forms.RadioSelect())
	number = forms.IntegerField(label='# of Pixels', required=False,widget=forms.NumberInput(attrs={'class': 'form-control'}))

	class Meta:
		model = PaymentNote
		fields = ['url', 'name', 'number']

		labels = {
			'url': 'URL (optional)'
		}

		widgets= {
			'url': forms.TextInput(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control'}),
		}

	def __init__(self, *args, **kwargs):
		self.picture = kwargs.pop('picture')
		super().__init__(*args, **kwargs)
		self.initial['number_preset'] = 5

	def clean(self):
		cleaned_data = super().clean()

		preset = cleaned_data.get('number_preset', '0') #presets aren't always used
		number = cleaned_data['number']

		if not preset or preset == '0':
			if not number or number <= 0:
				self.add_error('number', "Please enter a pixel amount!")

		else:
			number = cleaned_data['number'] = int(preset)

			if number and not self.picture.has_at_least_n_left_uncovered(int(number)):
				self.add_error('number', "Not enough pixels are left to process that request")

		return cleaned_data
