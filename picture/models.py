import itertools
import uuid
import random

from PIL import Image
from io import BytesIO

from picturepay.storage import OverwriteStorage

from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your models here.
def picture_path(instance, filename):
	return "pictures/{}/{}".format(uuid.uuid4(), filename)

def covered_picture_path(instance, filename):
	return "pictures/covered/{}".format(filename)

class Picture(models.Model):

	""" The picture model that will be uncovered"""

	image = models.ImageField(upload_to=picture_path, height_field='height', width_field='width')
	covered_image = models.ImageField(upload_to=covered_picture_path, storage=OverwriteStorage(), blank=True)

	width = models.PositiveIntegerField(blank=True)
	height = models.PositiveIntegerField(blank=True)

	uncovered = models.TextField(blank=True)

	def save(self, *args, **kwargs):

		if not self.pk:
			#make entire picture uncovered on creation
			self.uncovered = '0' * self.image_size

		super().save(*args, **kwargs)

	@property
	def	image_size(self):
		return self.width * self.height

	def chunks(self, s, n):
		"""Produce `n`-character chunks from `s`."""
		for start in range(0, len(s)-1, n):
			yield s[start:start+n]

	@property
	def uncovered_map(self):
		""" returns generator for a map-like structure of the uncovered image"""
		return self.chunks(self.uncovered, self.width)

	@property
	def uncovered_indices(self):
		""" returns a list of indices where uncovered is still 0 """
		return [i for i, x in enumerate(self.uncovered) if x == '0']

	def update_covered_image(self):
		""" save the new image from the uncovered data"""
		img = Image.open(BytesIO(self.image.read()))
		img_map = img.load()

		for i, row in enumerate(self.uncovered_map):
			for j, val in enumerate(row):
				if val == '0':
					img_map[j, i] = (0,0,0)

		buf = BytesIO()
		img.save(buf, format=img.format)

		self.covered_image = InMemoryUploadedFile(buf, None, self.image.name.split('/')[-1], 'image/jpeg', buf.getbuffer().nbytes, None)

		self.save()

	def uncover_random(self, number):
		""" uncover a random pixel any number of times """
		if number > 0:
			slist = list(self.uncovered)
			indices_to_uncover = random.sample(self.uncovered_indices, number)

			for i in indices_to_uncover:
				slist[i] = '1'

			self.uncovered = ''.join(slist)

		self.update_covered_image()
