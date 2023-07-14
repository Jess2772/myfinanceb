import os
from user_api.models import *
from datetime import datetime

def run():
    Categories.objects.create(name="Grocery", abbr="GC")
