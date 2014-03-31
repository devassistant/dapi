from dapi.models import MetaDap, Dap, Author
from django.contrib import admin


class MetaDapAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['package_name']}),
        ('Owner', {'fields': ['user', 'comaintainers']}),
        ('Active', {'fields': ['active']}),
        ('Latest versions', {'fields': ['latest', 'latest_stable'], 'classes': ['collapse']}),
        ('Tags', {'fields': ['tags']}),
    ]
    filter_horizontal = ['comaintainers']


admin.site.register(MetaDap, MetaDapAdmin)


class AuthorInline(admin.StackedInline):
    model = Author
    extra = 1


class DapAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Mandatory', {'fields': ['metadap', 'version', 'file', 'license', 'summary']}),
        ('Optional', {'fields': ['homepage', 'bugreports', 'description'], 'classes': ['collapse']}),
    ]
    inlines = [AuthorInline]


admin.site.register(Dap, DapAdmin)
