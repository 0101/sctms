from django.contrib import admin

from pages.models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = 'title', 'slug',
    search_fields = 'title', 'slug', 'content',


admin.site.register(Page, PageAdmin)
