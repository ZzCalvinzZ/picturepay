from django.contrib import admin
from picture.models import Picture

# Register your models here.

class PictureAdmin(admin.ModelAdmin):
	pass

admin.site.register(Picture, PictureAdmin)
