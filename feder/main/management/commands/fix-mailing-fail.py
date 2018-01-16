import argparse
import csv
from datetime import datetime
from django.core.management.base import BaseCommand

from feder.cases.models import Case, Alias
from feder.institutions.models import Institution
from feder.letters.models import Letter
from feder.monitorings.models import Monitoring
from feder.users.models import User


class Command(BaseCommand):
    help = "Fix mailing fail."

    def add_arguments(self, parser):
        parser.add_argument('--input', type=argparse.FileType('r'),
                            help="Report files that will be imported.", required=True)
        parser.add_argument('--username', help="Username of actor.", required=True)
        parser.add_argument('--monitoring-pk', help="PK of monitoring which receive mail", required=True)

    def handle(self, input, username, monitoring_pk, *args, **options):

        monitoring = Monitoring.objects.get(pk=monitoring_pk)
        user = User.objects.get(username=username)
        num = 0
        reader = csv.DictReader(input, fieldnames=['pos', 'date', 'mid', 'case_email', 'institution_email'])
        for row in reader:
            institution = Institution.objects.filter(email=row['institution_email']).first()

            case_qs = Case.objects.prefetch_related('alias_set').filter(institution=institution,
                                                                        monitoring=monitoring)
            case_count = case_qs.count()

            if case_count == 0:
                self.stdout.write('register-new-case %s %s' % (row['institution_email'], row['case_email']))
                postfix = " $%d" % num
                create_date = datetime.strptime(row['date'], "%Y %b %d %H:%M:%S").replace(year=2019)
                case = Case.objects.create(user=user,
                                           name=monitoring.name + postfix,
                                           monitoring=monitoring,
                                           institution=institution,
                                           email=row['case_email'])
                Letter.objects.create(author_user=user,
                                      case=case,
                                      is_draft=False,
                                      title=monitoring.subject,
                                      body=monitoring.template,
                                      created=create_date)
                num += 1
            elif case_count == 1:
                case = case_qs.get()
                if case.email == row['case_email']:
                    self.stdout.write('good %s %s' % (row['institution_email'], row['case_email']))
                else:
                    alias_founded = len([x for x in case.alias_set.all() if x.email == row['case_email']])
                    if alias_founded == 0:
                        self.stdout.write('register-alias %s %s' % (row['institution_email'], row['case_email']))
                        Alias.objects.create(case=case,
                                             email=row['case_email'])
                    else:
                        self.stdout.write('found-alias %s %s' % (row['institution_email'], row['case_email']))
            else:
                self.stdout.write('Case duplicated %s' % row['institution_email'])

            # pos, date, mid, case_email, institution_email=line.strip().split(';')
            # cases = Case.objects.by_addresses([case_email])
            # institution = Institution.objects.filter(email=institution_email)\
            #     .prefetch_related('tags').first()
            # len_cases = len(cases)
            #
            #
            # is_gmina = len([x for x in institution.tags.all() if x == tag]) == 1
            # if not is_gmina:
            #     self.stdout.write('Invalid mailing %s' % institution_email)

    # self.stdout.write('Finish my work')
