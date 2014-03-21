from dapi.models import Dap, Author
from django.contrib import admin

class AuthorInline(admin.StackedInline):
    model = Author
    extra = 3

class DapAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Mandatory', {'fields': ['package_name', 'version', 'license', 'summary']}),
        ('Optional',  {'fields': ['homepage', 'bugreports', 'description'], 'classes': ['collapse']}),
    ]
    inlines = [AuthorInline]

admin.site.register(Dap, DapAdmin)
