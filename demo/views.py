from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from demo.models import MultiLingualPage

def switch_to_en(request):
    return _switch_to_lang(request, 'en')

def switch_to_es(request):
    return _switch_to_lang(request, 'es')

def _switch_to_lang(request, dest_lang):
    '''
    Find the page object (should be a MultilingualPage) for the page
    that sent this POST and redirect to the matching page for the
    requested language.

    If no matching page is found, redirect to the home page for the
    destination language which should also be a MultilingualPage. 
    Loading a MultilingualPage is expected to set the session's
    language so that static translations also take affect.
    '''
    if request.method == 'POST':
        page_id = request.POST.get('requesting_page_id', None)
        if page_id is None:
            return

    page = get_object_or_404(MultiLingualPage, id=page_id)
    dest = '/' + dest_lang # default to homepage url

    if dest_lang == 'es' and page.is_english() and page.spanish_page() is not None:
        dest = page.spanish_page().url

    elif dest_lang == 'en' and page.is_spanish() and page.english_page() is not None:
        dest = page.english_page().url

    return HttpResponseRedirect(dest)
