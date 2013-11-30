import autofixture
import string
from datetime import datetime
from django.contrib.auth.models import User, UNUSABLE_PASSWORD
from autofixture import AutoFixture
from autofixture import generators
from django.core.management.base import BaseCommand, CommandError
from YAASApp.models import auction, bid
from django.utils import timezone
from django.contrib import auth


class Command(BaseCommand):

    def handle(self, *args, **options):

        fixture = AutoFixture(User, field_values={'username': generators.StringGenerator(max_length=10),'first_name':generators.FirstNameGenerator(), 'last_name':generators.LastNameGenerator(),
                                                  'email':generators.EmailGenerator(), 'password':UNUSABLE_PASSWORD})
        entries = fixture.create(50)

        for us in User.objects.all():
            if us.username != 'alberto':
                us.set_password('pass')
                us.save()

        fixture = AutoFixture(auction, field_values={
            'min_price': generators.PositiveSmallIntegerGenerator(max_value=1000), 'lock':False})
        entries = fixture.create(50)


        fixture = AutoFixture(bid, field_values={
            'amount': generators.IntegerGenerator(min_value=0), 'status':'W'})
        entries = fixture.create(20)

        auct = auction.objects.all()
        for auc in auct:
            if (auc.deadline > timezone.make_aware(datetime.now(), timezone.get_default_timezone())):
                auc.lifecycle = 'A'
                auc.save()
            if (auc.deadline < timezone.make_aware(datetime.now(), timezone.get_default_timezone()) and auc.lifecycle=='A'):
                auc.lifecycle = 'D'
                auc.save()

        bids = bid.objects.all()
        for b in bids:
            for a in bids:
                if (b.auct == a.auct and a != b):
                    if (b.status == 'W' and a.status == 'W'):
                        if (b.amount > a.amount):
                            a.status = 'L'
                            a.save()
                        else:
                            b.status = 'L'
                            b.save()
            if (b.amount < b.auct.min_price):
                b.amount = b.auct.min_price+1
                b.save()
            if (b.user == b.auct.seller):
                b.delete()