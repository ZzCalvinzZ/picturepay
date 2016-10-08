from django.shortcuts import render
from django.views.generic import TemplateView

from picture.models import Picture

# Create your views here.
class PictureView(TemplateView):
	template_name='picture/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Picture.objects.first()

		context['picture'].update_covered_image()

		return context

