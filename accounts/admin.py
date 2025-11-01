from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, WhatsAppVerification

admin.site.register(Profile)


@admin.register(WhatsAppVerification)
class WhatsAppVerificationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'encoded_code', 'numeric_code', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email', 'encoded_code', 'numeric_code')
    readonly_fields = ('created_at', 'verified_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

