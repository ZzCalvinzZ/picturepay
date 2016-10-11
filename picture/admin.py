from django.contrib import admin
from picture.models import Picture, Settings

# Register your models here.

class PictureAdmin(admin.ModelAdmin):
	pass

class SettingsAdmin(admin.ModelAdmin):
	pass

admin.site.register(Picture, PictureAdmin)
admin.site.register(Settings, SettingsAdmin)
