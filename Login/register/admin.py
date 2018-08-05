from django.contrib import admin
from .models import User,ConfirmString

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['name','email','sex','has_confirmed']
    search_fields = ['name']
    list_filter = ['c_time']

admin.site.register(User,UserAdmin)
admin.site.register(ConfirmString)