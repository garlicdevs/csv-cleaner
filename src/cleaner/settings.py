from django.conf import settings

from config.cfgutils import required

API_KEY = required(settings, "API_KEY")
