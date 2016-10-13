import itertools
import uuid
import random
import math

from PIL import Image
from io import BytesIO

from picturepay.storage import OverwriteStorage

from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile

class SquareTooBigException(Exception):
	pass

class NumberTooHighError(Exception):
	pass

class LessThanOneError(Exception):
	pass

class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.id=1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

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

	complete = models.BooleanField(default=False)

	def __str__(self):
		return "{}".format(self.image.name.split('/')[-1])

	def save(self, *args, **kwargs):

		if not self.pk:
			#make entire picture uncovered on creation
			self.uncovered = '0' * self.image_size
			super().save(*args, **kwargs)
			self.update_covered_image()

		else:
			super().save(*args, **kwargs)

	@property
	def	image_size(self):
		return self.width * self.height

	def chunks(self, s, n):
		"""Produce `n`-character chunks from `s`."""
		for start in range(0, len(s)-1, n):
			yield s[start:start+n]

	@property
	def uncovered_generator(self):
		""" returns generator for a map-like structure of the uncovered image """
		return self.chunks(self.uncovered, self.width)

	@property
	def uncovered_map(self):
		""" a 2d matrix representation of the uncovered map """
		map = []
		for i, row in enumerate(self.uncovered_generator):
			map_row = []
			for j, val in enumerate(row):
				map_row.append(val)
			map.append(map_row)

		return map

	def update_uncovered_from_map(self, map):
		string = ''

		for row in map:
			for val in row:
				string += val

		self.uncovered = string

	@property
	def uncovered_indices(self):
		""" returns a list of indices where uncovered is still 0 """
		return [i for i, x in enumerate(self.uncovered) if x == '0']

	def check_if_completely_uncovered(self):
		if self.uncovered.find('0') == -1:
			self.complete = True
			self.save()

	def update_covered_image(self):
		""" save the new image from the uncovered data"""
		self.image.open()
		img = Image.open(BytesIO(self.image.read()))
		img_map = img.load()

		for i, row in enumerate(self.uncovered_generator):
			for j, val in enumerate(row):
				if val == '0':
					img_map[j, i] = (0,0,0)

		buf = BytesIO()
		img.save(buf, format=img.format)

		self.covered_image = InMemoryUploadedFile(buf, None, self.image.name.split('/')[-1], 'image/jpeg', buf.getbuffer().nbytes, None)

		self.save()

		self.check_if_completely_uncovered()

	def uncover_random(self, number):
		""" uncover a random pixel any number of times """
		if number > 0:
			slist = list(self.uncovered)
			indices_to_uncover = random.sample(self.uncovered_indices, number)

			for i in indices_to_uncover:
				slist[i] = '1'

			self.uncovered = ''.join(slist)

			self.update_covered_image()

	def uncover_line(self, number):
		""" uncover a group of n pixels around one random point """
		if number < 1:
			raise LessThanOneError

		if self.uncovered.count('0') < number:
			raise NumberTooHighError

		slist = list(self.uncovered)
		index = random.choice(self.uncovered_indices)

		count = number
		while True:

			try:
				if slist[index] == '0':
					slist[index] = '1'
					count -= 1
			except IndexError as e:
				index = 0
				if slist[index] == '0':
					slist[index] = '1'
					count -= 1

			index += 1
			if count == 0:
				break

		self.uncovered = ''.join(slist)

		self.update_covered_image()

class Settings(SingletonModel):
	""" this is used to find which picture the site is using at the moment"""
	picture = models.ForeignKey(Picture)

	class Meta:
		verbose_name = "Settings"
		verbose_name_plural = "Settings"

class PaymentNote(models.Model):
	message = models.TextField(max_length=255, blank=True)
	url = models.TextField(max_length=255, blank=True)
	type = models.IntegerField()
	pixels = models.IntegerField()

	def __str__(self):
		return message
