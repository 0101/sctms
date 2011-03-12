#!/usr/bin/env python
from cms.models import BlogEntry, Category, Comment
from django.contrib import admin


admin.site.register(BlogEntry)
admin.site.register(Comment)
admin.site.register(Category)


