from django.contrib import admin
from .models import RecommendationVideo
from .models import Challenge, UserChallenge


admin.site.register(RecommendationVideo)
admin.site.register(Challenge)
admin.site.register(UserChallenge)
