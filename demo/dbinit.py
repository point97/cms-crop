"""
This will load the minimal data needed to create the site.

It loads 

1) The superuser

2) Pages


"""
from django.contrib.auth.models import User

from demo.models import *


user, created = User.objects.get_or_create(username='p97dev')
if created: 
    user.email="p97dev@pointnineseven.com"
    user.first_name="P97"
    user.last_name="Dev"
    user.is_staff=True
    user.is_superuser=True
            
    user.save()
    user.set_password("p97dev")
    user.save()
    print "Added p97dev superuser with password p97dev"

print "Creating Language Root"
root = Page.objects.get(slug='root')
children = root.get_children()
if not children.filter(slug='langroot'):
    rs = root.add_child(title='LangRoot', slug='langroot')

import pdb; pdb.set_trace()
print "Create English Home Page"
langroot = LangRootPage.objects.get(slug='langroot')
children = langroot.get_children()

if not children.filter(slug='en'):
    print "Adding english home page"
    langroot.add_child(title='Home', slug='en')

if not children.filter(slug='es'):
    print "Adding spanish home page"
    langroot.add_child(title='Casa', slug='es')



ENGLISH_PAGES = [
    {'slug':'learn', 'title':'Learn'},
    {'slug':'navigate', 'title':'Navigate'},
    {'slug':'contact', 'title':'Contact'},
    {'slug':'about', 'title':'About'},
    {'slug':'about2', 'title':'About2'},
]

for page in ENGLISH_PAGES:
    enHomePage  = EnglishHomePage.objects.get(slug='en')
    children = enHomePage.get_children()
    if not children.filter(slug=page['slug']):
        enHomePage.add_child(**page)