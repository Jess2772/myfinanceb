import os
from user_api.models import *
from datetime import datetime

def run():
    # t = Categories.objects.create(name="yo@gmail.com", abbr="yo")
    # t.save()
    s = Merchant.objects.create(category_id = Categories.objects.get(name="yo@gmail.com").category_id, merchant_name="asdf")

