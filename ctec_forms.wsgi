# -*- coding: utf-8 -*-
import os
import sys

sys.path.append('/srv/www/ctec-pet-christopher/ctec-forms')
#sys.setdefaultencoding('utf-8')

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/ctec-pet-christopher/ctec-forms/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'forms.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
