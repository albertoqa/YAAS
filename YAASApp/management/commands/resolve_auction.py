from django.core.management.base import BaseCommand, CommandError
from YAASApp.models import auction, bid
from django.core.mail import send_mail
from django.utils import timezone
import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):
        auct = auction.objects.all().filter(lifecycle='A')
        for auc in auct:
            if (auc.deadline - timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())).total_seconds() < 0:
                auc.lifecycle = 'D'
                auc.save()

                #self.stdout.write('Successfully due auction "%s"' % auc.id)

        auct = auction.objects.all().filter(lifecycle='D')
        for auc in auct:
            auc.lifecycle = 'X'
            auc.save()
            send_mail('Auction finished.', "Your auction has finished.", 'no_repli@yaas.com', [auc.seller.email,], fail_silently=False)

            mails = []
            bids = bid.objects.all().filter(auct=auc)
            for b in bids:
                if b.user.email in mails:
                    pass
                else:
                    mails.append(b.user.email)
            #print mails
            send_mail('Auction Finished.', "An auction in which you have bid on is over.", 'no_repli@yaas.com', mails, fail_silently=False)