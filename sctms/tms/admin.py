from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from tms.forms import TournamentForm, RulesForm
from tms.models import Map, Match, Player, Replay, Round, Tournament, Rules


class RoundInline(admin.StackedInline):
    model = Round
    extra = 0


class MatchInline(admin.TabularInline):
    model = Match
    raw_id_fields = 'player1', 'player2',
    extra = 0


class TournamentAdmin(admin.ModelAdmin):
    search_fields = 'name', 'slug',
    date_hierarchy = 'registration_deadline'
    inlines = RoundInline,
    filter_horizontal = 'map_pool',
    list_display = 'name', 'slug',
    exclude = 'owner', 'players',
    form = TournamentForm


class RoundAdmin(admin.ModelAdmin):
    inlines = MatchInline,
    list_display = 'description', 'tournament', 'start', 'end', 'type'
    list_filter = 'tournament',
    search_fields = 'tournament__name', 'description',
    ordering = 'order',


class PlayerAdmin(admin.ModelAdmin):
    exclude = 'user',
    list_display = 'user', 'character_name',
    ordering = 'user',

    def queryset(self, request):
        qs = super(PlayerAdmin, self).queryset(request)
        user = request.user
        if not user.is_superuser:
            qs = qs.filter(user=user)
        return qs

    def response_change(self, request, obj):
        default = super(PlayerAdmin, self).response_change(request, obj)
        if request.user.is_superuser:
            return default
        if request.POST.has_key("_continue"):
            return default
        return HttpResponseRedirect('/')


class ReplayAdmin(admin.ModelAdmin):
    list_display = '__unicode__', 'player1', 'player2', 'tournament', 'round',
    list_filter = ()
    search_fields = 'file',


class RulesAdmin(admin.ModelAdmin):
    form = RulesForm


admin.site.register(Map)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Replay, ReplayAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Rules, RulesAdmin)
