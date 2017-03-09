from django.core.management.base import BaseCommand
from django.utils.six.moves import input

from hashbrown.models import Switch
from hashbrown.utils import SETTINGS_KEY, is_active, get_defaults


class Command(BaseCommand):
    help = 'Creates / deletes feature switches in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            default=False,
            help='Delete switches in the database that are not in ' + SETTINGS_KEY,
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Delete switches without confirmation (implies --delete)',
        )

    def handle(self, *args, **kwargs):
        if kwargs['delete'] or kwargs['force']:
            self._delete_switches(force=kwargs['force'])

        self._create_switches()
        self.stderr.write('All switches up-to-date.')

    def _create_switches(self):
        create_switches(self.stderr)

    def _delete_switches(self, force=False):
        delete_switches(self.stderr, force=force)


def create_switches(stderr):
    """Create switches listed in HASHBROWN_SWITCH_DEFAULTS which aren't in
    the database yet.
    """
    defaults = get_defaults()
    installed_switches = set(Switch.objects.values_list('label', flat=True))
    missing_switches = set(defaults) - installed_switches

    for label in sorted(missing_switches):
        is_active(label)
        stderr.write('Created switch %r.' % label)

    return missing_switches


def delete_switches(stderr, force=False):
    defaults = get_defaults()
    installed_switches = set(Switch.objects.values_list('label', flat=True))
    unknown_switches = sorted(installed_switches - set(defaults))

    if not unknown_switches:
        return

    permission_granted = force or ask_permission(stderr, unknown_switches)

    if permission_granted:
        Switch.objects.filter(label__in=unknown_switches).delete()

        for label in unknown_switches:
            stderr.write('Deleted switch %r.' % label)


def ask_permission(stderr, switches):
    stderr.write('The following switches are in the database but not in %s:' % SETTINGS_KEY)

    for label in switches:
        stderr.write(label)

    response = input('Delete switches? [y/N]: ')

    return response.lower().strip() in ('y', 'yes')
