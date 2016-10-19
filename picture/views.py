from PIL import Image

import stripe
import datetime

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.conf import settings

from paypal.standard.forms import PayPalPaymentsForm

from picture.models import Picture, Settings, Pixel, PaymentNote
from picture.forms import PaymentNoteForm

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received, payment_was_flagged


# Create your views here.
class PictureIndexView(FormView):
	template_name = 'picture/index.html'
	form_class = PaymentNoteForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Settings.objects.first().picture
		context['random'] = datetime.datetime.now()
		context['payment_notes'] = [{
			'name': note.name,
			'url': note.url,
			'number': note.number,
			'pixels': [{
				'r': pixel.r,
				'g': pixel.g,
				'b': pixel.b,
				} for pixel in note.pixels.all()[:50]]
		} for note in PaymentNote.objects.filter(picture=self.picture).order_by('-number')]


		return context

	def form_valid(self, form):
		note = form.save(commit=False)

		self.request.session['payment_note'] = {
			'name': note.name,
			'url': note.url,
			'number': note.number,
		}

		return super().form_valid(form)

	def dispatch(self, request, *args, **kwargs):
		self.picture = Settings.objects.first().picture
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['picture'] = self.picture
		return kwargs

	def get_success_url(self):
		if getattr(settings,'NO_PAYMENTS', False) == True:

			create_payment_note(self.request.session['payment_note'])

			return reverse('picture-payment-success')
		else:
			return reverse('picture-payment')

class PaymentView(TemplateView):
	template_name = 'picture/payment.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['picture'] = Settings.objects.first().picture
		context['paypal_form'] = self.paypal_form
		context['stripe'] = self.stripe_options
		context['amount'] = self.request.session.get('payment_note').get('number')

		return context

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		self.picture = Settings.objects.first().picture

		business = settings.PAYPAL_EMAIL

		paypal_options = {
			"business": business,
			"amount": request.session.get('payment_note').get('number'),
			"invoice": request.session.get('payment_note').get('url'),
			"custom": request.session.get('payment_note').get('name'),
			"item_name": "Pixel Reveal",
			# "invoice": "unique-invoice-id",
			"notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
			"return_url": request.build_absolute_uri(reverse('picture-payment')),
			"cancel_return": request.build_absolute_uri(reverse('picture-index')),
		}

		self.paypal_form = PayPalPaymentsForm(initial=paypal_options)

		#STRIPE stuff
		self.stripe_options = {
			'p_key': settings.STRIPE_PUBLISH,
			'amount': request.session.get('payment_note').get('number') * 100,
			'name': 'Calvin Collins',
			'description': 'Pixel Reveal',
		}

		return super().dispatch(request, *args, **kwargs)

class PaymentSuccessView(TemplateView):
	template_name = 'picture/payment_success.html'

class PaymentErrorView(TemplateView):
	template_name = 'picture/payment_error.html'

class StripeView(View):

	def post(self, request, *args, **kwargs):
		self.picture = Settings.objects.first().picture

		stripe.api_key = settings.STRIPE_SECRET

		token = request.POST['stripeToken']

		try:
			charge = stripe.Charge.create(
				amount = request.session.get('payment_note').get('number') * 100,
				currency="usd",
				source=token,
				description="Pixel Reveal"
				)
		except stripe.error.CardError as e:
			# The card has been declined
			return redirect(reverse('picture-payment-error'))

		else:
			create_payment_note(self.request.session['payment_note'])
			return redirect(reverse('picture-payment-success'))

def create_payment_note(note_info):

	form = PaymentNoteForm(note_info, picture=Settings.objects.first().picture)

	if form.is_valid():
		note = form.save(commit=False)
		note.picture = Settings.objects.first().picture
		note.save()

		coords = note.picture.uncover_line(note.number)

		img = note.picture.pillow_image.convert('RGB')

		for i, coord in enumerate(coords):
			if i > 50:
				break

			r, g, b = img.getpixel((coord['x'], coord['y']))

			note.pixels.add(Pixel.objects.create(
				x = coord['x'],
				y = coord['y'],
				r = r,
				g = g,
				b = b
			))

		note.save()

def handle_payment(sender, **kwargs):
	ipn_obj = sender
	if ipn_obj.payment_status == ST_PP_COMPLETED:
		# WARNING !
		# Check that the receiver email is the same we previously
		# set on the business field request. (The user could tamper
		# with those fields on payment form before send it to PayPal)
		if ipn_obj.receiver_email != "calvincollins_5-facilitator@hotmail.com":
			# Not a valid payment
			return

		note_info = {
			'name': ipn_obj.custom,
			'url': ipn_obj.invoice,
			'number': ipn_obj.mc_gross,
		}

		create_payment_note(note_info)

valid_ipn_received.connect(handle_payment)
