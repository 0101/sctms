#!/usr/bin/env python
from blog.models import Topic, Category, BlogEntry
from django.contrib import admin



admin.site.register(Topic)
admin.site.register(Category)
admin.site.register(BlogEntry)

