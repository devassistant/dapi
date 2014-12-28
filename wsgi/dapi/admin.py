from dapi import models
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


admin.site.register(models.MetaDap, MetaDapAdmin)


class AuthorInline(admin.StackedInline):
    model = models.Author
    extra = 1


class AssistantInline(admin.StackedInline):
    model = models.Assistant
    extra = 1


class DependencyInline(admin.StackedInline):
    model = models.Dependency
    extra = 1


class DapAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Mandatory', {'fields': ['metadap', 'version', 'file', 'sha256sum', 'license', 'summary', 'has_assistants']}),
        ('Optional', {
            'fields': ['homepage', 'bugreports', 'description', 'supported_platforms'],
            'classes': ['collapse'],
        }),
    ]
    inlines = [AuthorInline, AssistantInline, DependencyInline]


admin.site.register(models.Dap, DapAdmin)

admin.site.register(models.Rank)
admin.site.register(models.Profile)


class ReportAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Dap', {'fields': ['metadap', 'versions']}),
        ('Reporter', {'fields': ['reporter', 'email']}),
        ('Report', {'fields': ['problem', 'message', 'solved']}),
    ]
    filter_horizontal = ['versions']


admin.site.register(models.Report, ReportAdmin)


class PlatformAdmin(admin.ModelAdmin):
    fieldsets = [('Platform', {'fields': ['platform']})]

admin.site.register(models.Platform, PlatformAdmin)
