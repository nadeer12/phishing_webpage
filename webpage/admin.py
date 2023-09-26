from django.contrib import admin


from .models import blacklist 
from .models import Message
# Register your models here.

class blacklistAdmin(admin.ModelAdmin):
    list_display = ('no','url_name')

admin.site.register(blacklist,blacklistAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('user_name','user_email','user_message')

admin.site.register(Message,MessageAdmin)
