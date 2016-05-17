from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Node

class NodeAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'cert', 'address')

admin.site.register(Node, NodeAdmin)