# coding: utf-8
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model
from m3_fias.helpers import translate_kladr_codes


class Command(BaseCommand):
    args = '<app_name model_name field1 field2... fieldN>'
    help = 'Converts KLADR codes in database to FIAS GUIDs.'

    def handle(self, *args, **kwargs):
        app_name, model_name = args[:2]
        model = get_model(app_name, model_name)
        field_names = args[2:]

        translate_kladr_codes(model.objects.all(), field_names,
                              clean_invalid=True)
