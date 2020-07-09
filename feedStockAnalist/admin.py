from django.contrib import admin

# Register your models here.
from .models import Analysis

class AnalysisAdmin(admin.ModelAdmin):
    fields = ['created_at', 'created_by']

admin.site.register(Analysis, AnalysisAdmin)
