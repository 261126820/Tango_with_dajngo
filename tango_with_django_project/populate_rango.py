import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','tango_with_django_project.settings')

import django
django.setup()
from rango.models import Category, Page

def populate():
    # First, we will create lists of dictionaries containing the pages
    # We want to add into each category
    # Then we'll create a dictionary of dictionaries for our categories
    python_pages = [
        {'title': 'Official python tutorial', 
        'url': 'http://docs.python.org/3/tutorial/'},
        {'title': 'How to think like a computer science',
        'url': 'http://www.greenteapress.com/thinkpython/'},
        {'title': 'Learn python in 10 minutes',
        'url':'http://www.korokithakis.net/tutorials/python/'}
    ]

    django_pages = [
        {'title':'Official Django Tutorial',
        'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/'},
        {'title':'Django Rocks',
        'url':'http://www.djangorocks.com/'},
        {'title':'How to Tango with Django',
        'url':'http://www.tangowithdjango.com/'}  ]
    
    other_pages = [
        {'title':'Bottle','url':'http://bottlepy.org/docs/dev/'},
        {'title':'Flask', 'url':'http://www.tangowithdjango.com/'}]

    cats = {'Python':{'pages':python_pages, 'views':int(128), 'likes':int(64)},
            'Django':{'pages':django_pages, 'views':int(64), 'likes':int(32)},
            'Other Frameworks':{'pages':other_pages, 'views':int(32), 'likes':int(16)}
            }
        
    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data['views'], cat_data['likes'])
        for p in cat_data['pages']:
            add_page(c, p['title'], p['url'])
    
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print('- {0} -{1}'.format(str(c),str(p)))

# Create pages
def add_page(cat,title,url,views=0):
    # Check if objects have been created. If not, create it. Or return it.
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p
# Create categories
def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name = name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c

if __name__ == '__main__':
    print('Starting rango population')
    populate()

