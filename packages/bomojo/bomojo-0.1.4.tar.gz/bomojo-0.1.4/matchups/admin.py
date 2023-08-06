# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from matchups.models import Matchup


class MatchupAdmin(admin.ModelAdmin):
	list_display = ('title', 'email', 'description', 'featured', 'created_on')


admin.site.register(Matchup, MatchupAdmin)
