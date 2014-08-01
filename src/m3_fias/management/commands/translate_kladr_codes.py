#coding: utf-8

from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model

from django.conf import settings

import requests
import sys
import time


BATCH_SIZE = 100


class Command(BaseCommand):
    args = '<app_name model_name field1 field2... fieldN>'
    help = 'Converts KLADR codes in database to FIAS GUIDs.'

    def handle(self, *args, **kwargs):
        def is_num(val):
            return all([c >= '0' and c <= '9' for c in val])

        if len(args) < 3:
            raise CommandError('You should specify app, model and at least one field to convert!')

        app_name, model_name = args[:2]
        model = get_model(app_name, model_name)
        field_names = args[2:]
        total_records = model.objects.count()

        for field in field_names:
            sys.stdout.write(u'Translating field "{0}"...\n'.format(field))

            codes = model.objects.exclude(**{field: ''})\
                                 .values_list(field, flat=True)\
                                 .distinct()
            codes = filter(lambda x: x and len(x) < 36 and is_num(x), list(codes))
            total_codes = len(codes)
            processed = 0
            records_updated = 0

            while codes:
                batch = codes[:BATCH_SIZE]
                codes = codes[BATCH_SIZE:]
                resp = requests.post(settings.FIAS_API_URL + '/translate',
                                     data=dict(kladr=batch))

                if not resp.json()['total']:
                    continue

                sys.stdout.write(u'{0} translations found for {1} codes.\n'.format(resp.json()['total'], len(batch)))
                for (kladr_code, fias_code) in resp.json()['codes'].iteritems():
                    t1 = time.time()
                    updated = model.objects.filter(**{field: kladr_code})\
                                           .update(**{field: fias_code})
                    t2 = time.time()
                    records_updated += updated
                    processed += 1
                    sys.stdout.write(u'[{0}s, {4}/{5} codes, {6}/{7} recs] {1} => {2} ({3} records)\n'.format(
                        int(t2 - t1), kladr_code, fias_code, updated, processed, total_codes,
                        records_updated, total_records))
                sys.stdout.write('\n')