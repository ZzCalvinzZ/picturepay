from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View

from picture.models import Picture, Settings

# Create your views here.
class PictureView(TemplateView):
	template_name='picture/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Settings.objects.first().picture

		return context

class NumberPixelView(View):

	"""get the number of pixels"""
	def dispatch(self, request, *args, **kwargs):
		self.number = request.POST.get('number')

		self.picture = Settings.objects.first().picture

		return super().dispatch(request, *args, **kwargs)

class RandomUnveilView(NumberPixelView):

	def post(self, request, *args, **kwargs):
		self.picture.uncover_random(int(self.number))

		return redirect('picture-index')

class LineUnveilView(NumberPixelView):

	def post(self, request, *args, **kwargs):
		self.picture.uncover_line(int(self.number))

		return redirect('picture-index')
