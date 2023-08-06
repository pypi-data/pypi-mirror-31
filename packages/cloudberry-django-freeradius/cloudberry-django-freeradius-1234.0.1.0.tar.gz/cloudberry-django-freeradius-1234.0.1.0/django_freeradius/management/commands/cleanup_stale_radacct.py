from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from django_freeradius.models import RadiusAccounting


class Command(BaseCommand):
    help = "Closes active accounting sessions older than <days>"

    def add_arguments(self, parser):
        parser.add_argument('number_of_days', type=int, nargs='?', default=15)

    def handle(self, *args, **options):
        days = now() - timedelta(days=options['number_of_days'])
        sessions = RadiusAccounting.objects.filter(start_time__lt=days, stop_time=None)
        for session in sessions:
            # calculate seconds in between two dates
            session.session_time = (now() - session.start_time).total_seconds()
            session.stop_time = now()
            session.update_time = session.stop_time
            session.save()
        self.stdout.write('Closed active sessions older than {} days'.format(options['number_of_days']))
