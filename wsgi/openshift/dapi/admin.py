from dapi.models import Dap, Author
from django.contrib import admin


class AuthorInline(admin.StackedInline):
    model = Author
    extra = 1

class DapAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Mandatory', {'fields': ['package_name', 'version', 'license', 'summary', 'user']}),
        ('Optional', {'fields': ['homepage', 'bugreports', 'description', 'comaintainers'], 'classes': ['collapse']}),
    ]
    filter_horizontal = ['comaintainers']
    inlines = [AuthorInline]

admin.site.register(Dap, DapAdmin)
