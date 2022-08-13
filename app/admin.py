from django.contrib import admin

from .models import Plan, UserPlan

admin.site.register(Plan)
admin.site.register(UserPlan)