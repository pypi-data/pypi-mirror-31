# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from bomojo.matchups.forms import MatchupForm
from bomojo.matchups.models import Matchup
from bomojo.utils import get_avatar_url


class MatchupsView(View):
    def get(self, request):
        featured_matchups = Matchup.objects.filter(featured=True)
        recent_matchups = featured_matchups.order_by('-created_on')[:20]
        return JsonResponse([_render_matchup(matchup)
                             for matchup in recent_matchups], safe=False)

    @method_decorator(login_required)
    def post(self, request):
        form = MatchupForm(request, request.JSON)
        if form.is_valid():
            matchup = form.save()
            return JsonResponse(_render_matchup(matchup), status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)


class MatchupView(View):
    @method_decorator(cache_page(60 * 60))
    def get(self, request, slug):
        try:
            matchup = Matchup.objects.get(slug=slug)
            return JsonResponse(_render_matchup(matchup))
        except Matchup.DoesNotExist:
            return JsonResponse({
                'errors': {
                    'slug': ['That matchup does not exist.']
                }
            }, status=404)

    @method_decorator(login_required)
    def put(self, request, slug):
        try:
            matchup = request.user.matchups.get(slug=slug)
        except Matchup.DoesNotExist:
            return JsonResponse({
                'errors': {
                    'slug': ['That matchup does not exist.']
                }
            }, status=404)

        data = model_to_dict(matchup)
        data.update(request.JSON)

        form = MatchupForm(request, data, instance=matchup)
        if form.is_valid():
            matchup = form.save()
            return JsonResponse(_render_matchup(matchup), status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)


def _render_matchup(matchup):
    result = {
        'slug': matchup.slug,
        'title': matchup.title,
        'description': matchup.description,
        'avatar': '',
        'movies': matchup.movies,
        'period': matchup.period,
        'created': matchup.created_on.isoformat()
    }

    if matchup.user.email:
        result['avatar'] = get_avatar_url(matchup.user.email)

    return result
