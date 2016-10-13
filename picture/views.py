from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, FormView
from django.core.urlresolvers import reverse_lazy

from picture.models import Picture, Settings, PaymentNote
from picture.forms import PaymentNoteForm

# Create your views here.
class PictureIndexView(FormView):
	template_name = 'picture/index.html'
	form_class = PaymentNoteForm
	success_url = reverse_lazy('picture-index')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Settings.objects.first().picture
		context['payment_notes'] = [{
			'name': note.name,
			'message': note.message,
			'number': note.number,
		} for note in PaymentNote.objects.filter(picture=self.picture).order_by('-number')]

		return context

	def form_valid(self, form):
		note = form.save(commit=False)
		note.picture = self.picture
		note.save()

		self.picture.uncover_line(note.number)
		return super().form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		self.picture = Settings.objects.first().picture
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['picture'] = self.picture
		return kwargs
