from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from feder.cases.models import Case, Alias
from feder.institutions.models import Institution, Tag
from feder.letters.models import Letter
from feder.monitorings.models import Monitoring
from feder.users.models import User


class Command(BaseCommand):
    help = "Fix mailing fail."


    def handle(self,  *args, **options):
        current_monitoring = Monitoring.objects.get(pk=9)
        user = User.objects.first()
        # tag = Tag.objects.filter(name__contains="gminy").first()
        num = 0;
        with open('wyniki-gminy.csv') as f:
            for line in f:

                pos, date, mid, case_email, institution_email=line.strip().split(';')

                institution = Institution.objects.filter(email=institution_email).first()

                cases = Case.objects.filter(institution=institution, monitoring=current_monitoring)\
                    .prefetch_related('alias_set')\
                    .all()

                # self.stdout.write('%s %s' % (len(cases), institution_email))
                if len(cases) == 0:
                    self.stdout.write('register-new-case %s %s' % (institution_email, case_email))
                    postfix = " $%d" % num
                    create_date = datetime.strptime(date, "%b %d %H:%M:%S").replace(year=2019)
                    case = Case(user=user,
                                name=current_monitoring.name + postfix,
                                monitoring=current_monitoring,
                                institution=institution,
                                email=case_email)
                    case.save()
                    letter = Letter(author_user=user,
                                    case=case,
                                    title=current_monitoring.subject,
                                    body=current_monitoring.template,
                                    created=create_date)
                    letter.save()
                    num += 1
                elif len(cases) == 1:
                    case = cases[0]
                    if case.email == case_email:
                        self.stdout.write('good %s %s' % (institution_email, case_email))
                    else:
                        alias_founded = len([x for x in case.alias_set.all() if x.email == case_email])
                        if alias_founded == 0:
                            self.stdout.write('register-alias %s %s' % (institution_email, case_email))
                            Alias(case=case, email=case_email).save()
                        else:
                            self.stdout.write('found-alias %s %s' % (institution_email, case_email))
                else:
                    self.stdout.write('Case duplicated %s' % institution_email)




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

