from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View

from picture.models import Picture

# Create your views here.
class PictureView(TemplateView):
	template_name='picture/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Picture.objects.first()

		context['picture'].update_covered_image()

		return context

class RandomUnveilView(View):

	def post(self, request, *args, **kwargs):

		number = request.POST.get('number')

		picture = Picture.objects.first()
		picture.uncover_random(int(number))

		return redirect('picture-index')
