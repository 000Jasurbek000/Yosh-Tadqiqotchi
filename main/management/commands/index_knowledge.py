from django.core.management.base import BaseCommand
from main.knowledge.ingest import rebuild_index


class Command(BaseCommand):
    help = 'Yosh Tadqiqotchi AI knowledge base ni indekslash (DB + template + business logic)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Eski barcha chunklarni o\'chirib, to\'liq qayta indeks',
        )

    def handle(self, *args, **options):
        self.stdout.write('Indexing knowledge base...')
        stats = rebuild_index(full=options['full'])
        for k, v in stats.items():
            self.stdout.write(f'  {k}: {v}')
        self.stdout.write(self.style.SUCCESS('Done.'))
