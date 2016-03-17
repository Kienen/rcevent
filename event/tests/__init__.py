from django.core.management import call_command

call_command("loaddata", 'sites.json', verbosity=1)