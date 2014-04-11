from modeltranslation.translator import translator, TranslationOptions
from demo.models import StandardPage

class StandardPageTranslationOptions(TranslationOptions):
    fields = ('title', 'intro', 'body',)

translator.register(StandardPage, StandardPageTranslationOptions)