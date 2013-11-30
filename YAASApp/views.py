from django.shortcuts import render_to_response
from django.template import RequestContext
from YAASApp.models import auction, bid
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib import auth
from YAASApp.forms import *
from django.core.mail import send_mail
import datetime
from django.utils.translation import ugettext as _
from django.utils import translation
from rest_framework.parsers import JSONParser
from django.forms import model_to_dict
import json
from YAASApp.serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponseNotFound

##################################################################################

def home(request):
    posts = auction.objects.all()
    return render_to_response("home.html", {'posts': posts},
    context_instance= RequestContext(request))

def login(request):
    if request.user.is_authenticated():
        mesg = _("User logged in. Log out before log in with a new user.")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg':mesg, 'posts': posts}, context_instance= RequestContext(request))

    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    posts = auction.objects.all()
                    mesg = _("Log in succesfull")
                    return render_to_response("home.html", {'msg': mesg, 'posts': posts},
                    context_instance= RequestContext(request))
            else:
                posts = auction.objects.all()
                mesg = _("Log in fail")
                return render_to_response("home.html", {'msg': mesg, 'posts': posts},
                context_instance= RequestContext(request))
        else:
            error = _("Please Sign in")
            return render_to_response("login.html", {'error': error},context_instance= RequestContext(request))
        return render_to_response("login.html", {},context_instance= RequestContext(request))

def register (request):
    if request.method == 'POST':
        form =UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()

            posts = auction.objects.all()
            mesg = _("New User is created. Please Login")
            return render_to_response("home.html", {'msg': mesg, 'posts': posts},
            context_instance= RequestContext(request))
    else:
        form =UserCreateForm(request.POST)

    return render_to_response("registration.html", {'form': form},context_instance= RequestContext(request))

def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
        posts = auction.objects.all()
        mesg = _("Log out sucesfull")
        return render_to_response("home.html", {'msg': mesg, 'posts': posts},
        context_instance= RequestContext(request))
    else:
        posts = auction.objects.all()
        mesg = _("No user loged in")
        return render_to_response("home.html", {'msg': mesg, 'posts': posts},
        context_instance= RequestContext(request))

def edit_user_info(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            password = request.POST['password']
            email = request.POST['email']

            #if email_re.match(email):
            if email != "":
                request.user.email = email
            if password != "":
                request.user.set_password(password)
            request.user.save()

            mesg = _("User Info edited")
            posts = auction.objects.all()
            return render_to_response("home.html", {'msg':mesg, 'posts': posts}, context_instance= RequestContext(request))

    else:
        mesg = _("You have to log in first")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

    return render_to_response("edituser.html", {},context_instance= RequestContext(request))

def add_auction(request):
    if request.user.is_authenticated():
        if not request.method == 'POST':
            form = createAuction()
            return render_to_response('add_auction.html', {'form' : form}, context_instance=RequestContext(request))

        else:
            form = createAuction(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                title = cd['title']
                description = cd['description']
                deadline = cd['deadline'].strftime("%d/%m/%Y %H:%M:%S")
                min_price = cd['min_price']

                d = datetime.datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")

                if (d - datetime.datetime.now()).total_seconds() < 259200:
                    mesg = _("The minimun duration of an auction is 72hours. You have to change the deadline.")
                    form = createAuction()
                    return render_to_response('add_auction.html', {'msg': mesg, 'form': form}, context_instance=RequestContext(request))

                form = confAuction()
                return render_to_response('wizardTest.html', {'form' : form, "title" : title, "description" : description, "deadline": deadline,
                                                                "min_price": min_price}, context_instance=RequestContext(request))
            else:
                form = createAuction()
                return render_to_response('add_auction.html', {'form' : form, "error" : _("Not valid data") },
                                          context_instance=RequestContext(request))
    else:
        mesg = _("You have to log in first")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def save_auction(request):
    if request.user.is_authenticated():
        option = request.POST.get('option', '')
        if option == 'Yes':
            new_title = request.POST['title']
            new_description = request.POST['description']
            new_deadline = datetime.datetime.strptime(request.POST.get('deadline', ''),"%d/%m/%Y %H:%M:%S")
            #in spanish numbers have a comma not a dot
            new_min_price = float(request.POST.get('min_price', '').replace(',', '.'))
            new_seller = request.user
            a = auction(title=new_title, description=new_description, deadline=new_deadline, min_price=new_min_price, seller=new_seller, lifecycle='A')
            a.save()
            send_mail('New auction created.', "Your new auction has been created successfully.", 'no_repli@yaas.com', [request.user.email,], fail_silently=False)
            mesg = _("New auction has been saved and a confirmation email has been sent to your email.")
            return render_to_response('done.html', {'mesg' : mesg},context_instance=RequestContext(request))
        else:
            error = _("Auction is not saved")
            form = createAuction()
            return render_to_response('add_auction.html', {'form' : form, 'error' : error},
                                      context_instance=RequestContext(request))
    else:
        mesg = _("You have to log in first")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def edit_auction(request, id):
    if not request.user.is_authenticated():
        mesg = _("You have to log in first")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
    else:
        if id:
                auct = auction.objects.filter(id = id)
                if auct:
                    auct = auction.objects.get(id = id)
                    if auct.seller == request.user:
                        if auct.lifecycle == 'A':

                            title = auct.title
                            description = auct.description
                            deadline = auct.deadline
                            min_price = auct.min_price
                            #auct.version = auct.version+1
                            auct.lock = True
                            auct.save()
                            return render_to_response("edit_auction.html",
                                          {'user' : request.user, "title" : title, "id": auct.id, "description": description,
                                           "deadline": deadline, "min_price": min_price}, context_instance=RequestContext(request))
                        else:
                            mesg = _("This auction is not active, you can not edit it.")
                            posts = auction.objects.all()
                            return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
                    else:
                        mesg = _("You can not edit auctions from other sellers.")
                        posts = auction.objects.all()
                        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
                else:
                    mesg = _("Auction not found.")
                    posts = auction.objects.all()
                    return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
        else:
            posts = auction.objects.all()
            return render_to_response("home.html", {'posts' : posts, "msg" : "No auction selected" }, context_instance=RequestContext(request))

def save_edited_auction(request, id):
    auct= auction.objects.get(id = id)
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    min_price = float(request.POST.get('min_price', '').replace(',', '.'))
    deadline = datetime.datetime.strptime(request.POST.get('deadline', ''),"%d/%m/%Y %H:%M")

    if (deadline - datetime.datetime.now()).total_seconds() < 259200:
        mesg = _("The minimun duration of an auction is 72hours. You have to change the deadline.")
        return render_to_response("edit_auction.html",
                                {'user' : request.user, 'error': mesg}, context_instance=RequestContext(request))

    auct.title = title
    auct.description = description
    auct.min_price = min_price
    auct.deadline = deadline
    #auct.version = auct.version+1
    auct.lock = False
    auct.save()

    mesg = _("Auction edited.")
    posts = auction.objects.all()
    return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def canceledit(request, id):
    auct = auction.objects.get(id = id)
    auct.lock = False
    auct.save()
    mesg = _("Auction not edited.")
    posts = auction.objects.all()
    return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def view_auction(request, id):
    auct = auction.objects.filter(id = id)
    if auct:
        auct = auction.objects.get(id = id)

        if auct.lock == True:
            return render_to_response("lock.html", context_instance = RequestContext(request))

        bb = bid.objects.filter(status='W', auct=auct)
        if bb:
            bb = bid.objects.filter(status='W', auct=auct).get()
        return render_to_response("auction.html", {'auct': auct, 'bb': bb}, context_instance= RequestContext(request))
    else:
        mesg = _("Auction not found.")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def ban_auction(request, id):
    if request.user.is_superuser:
        auct = auction.objects.filter(id = id)
        if auct:
            auct = auction.objects.get(id = id)
            auct.lifecycle = 'B'
            auct.save()
            send_mail('Auction Banned.', "Your auction has been baned.", 'no_repli@yaas.com', [auct.seller.email,], fail_silently=False)

            mails = []
            bids = bid.objects.all().filter(auct=auct)
            for b in bids:
                if b.user.email in mails:
                    pass
                else:
                    mails.append(b.user.email)
            #print mails
            send_mail('Auction Banned.', "An auction in which you have bid on has been banned.", 'no_repli@yaas.com', mails, fail_silently=False)

            mesg = _('Auction banned.')
            posts = auction.objects.all()
            return render_to_response("home.html", {'posts': posts, 'msg': mesg}, context_instance= RequestContext(request))
        else:
            mesg = _("Auction not found.")
            posts = auction.objects.all()
            return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
    else:
        mesg = _("You have to be the admin for ban an auction.")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

def changelang(request):
    if request.method == 'POST':
        request.session['django_language'] = request.POST['lang']
        translation.activate(request.session["django_language"])

    posts = auction.objects.all()
    mesg = _("Languaje changed")
    return render_to_response("home.html", {'msg': mesg, 'posts': posts},
                context_instance= RequestContext(request))

def search(request, tit=''):

    if request.method == 'POST':
        tit = request.POST['tit']

    auctions = auction.objects.all().filter(title__contains=tit).exclude(lifecycle='B')
    if len(auctions) < 1 and tit!='':
        mesg = _("Auction not found.")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))
    elif len(auctions) == 1:
        auct = auctions.get()
        bb = bid.objects.filter(status='W', auct=auct)
        if bb:
            bb = bid.objects.filter(status='W', auct=auct).get()
        return render_to_response("auction.html", {'auct': auct, 'bb': bb}, context_instance= RequestContext(request))
    elif len(auctions) > 1 and tit=='':
        posts = auction.objects.all()
        return render_to_response("home.html", {'posts': posts}, context_instance= RequestContext(request))
    else:
        return render_to_response("home.html", {'posts': auctions}, context_instance= RequestContext(request))

def bid_auction(request, id):
    if request.user.is_authenticated():
        if request.method == 'POST':

            amount = request.POST['am']
            auct = auction.objects.filter(id=id)
            if auct:
                auct = auction.objects.get(id=id)
            else:
                msg = "Auction not found"
                return render_to_response("auction.html", {'msg': msg}, context_instance= RequestContext(request))

            if auct.lock == True:
                return render_to_response("lock.html", context_instance = RequestContext(request))

            if auct.lifecycle != 'A':
                msg = "Auction not active"
                return render_to_response("auction.html", {'auct':auct, 'msg': msg}, context_instance= RequestContext(request))
            if request.user == auct.seller:
                msg = "Can not bid on your own auction"
                return render_to_response("auction.html", {'auct':auct, 'msg': msg}, context_instance= RequestContext(request))
            if auct.min_price > float(amount) or (float(amount) - auct.min_price < 0.01):
                msg = "Amount have to be at least 0.01 bigger than minimum price."
                return render_to_response("auction.html", {'auct':auct, 'msg': msg}, context_instance= RequestContext(request))

            prev_bid_wining = bid.objects.filter(status='W', auct=auct)
            if prev_bid_wining:
                prev_bid_wining = bid.objects.filter(status='W', auct=auct).get()

            #in case that exists
            if prev_bid_wining:
                if prev_bid_wining.user == request.user:
                    msg = "You are already wining this auction."
                    return render_to_response("auction.html", {'auct':auct,'bb':prev_bid_wining, 'msg': msg}, context_instance= RequestContext(request))

                if float(amount) - prev_bid_wining.amount < 0.01:
                    msg = "Bid has to be at less 0.01 bigger than previous bids."
                    return render_to_response("auction.html", {'auct':auct,'bb':prev_bid_wining, 'msg': msg}, context_instance= RequestContext(request))

                send_mail('Bid losing.', "Somebody bid in the same auction that you did.", 'no_repli@yaas.com', [prev_bid_wining.user.email,], fail_silently=False)
                prev_bid_wining.status = 'L'
                prev_bid_wining.save()

            b = bid(user=request.user, amount=float(amount), auct=auct, status='W')
            b.save()

            #Optional feature: soft deadlines
            deadline = auct.deadline.strftime("%d/%m/%Y %H:%M:%S")
            d = datetime.datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")

            if (d - datetime.datetime.now()).total_seconds() < 350:
                auct.deadline = auct.deadline + datetime.timedelta(seconds = 350)
                auct.save()

            send_mail('New bid in your auction.', "Somebody bid in the one of your auctions.", 'no_repli@yaas.com', [auct.seller.email,], fail_silently=False)
            send_mail('Bid accepted.', "Your new bed has been acepted.", 'no_repli@yaas.com', [request.user.email,], fail_silently=False)

            msg = "Bid saved sucesfully."
            return render_to_response("auction.html", {'auct':auct,'bb':b, 'msg': msg}, context_instance= RequestContext(request))

        else:
            auct = auction.objects.filter(id=id)
            if auct:
                auct = auction.objects.get(id=id)
            else:
                msg = "Auction not found"
                return render_to_response("auction.html", {'msg': msg}, context_instance= RequestContext(request))

            b = bid.objects.filter(status='W', auct=auct)
            if b:
                b = bid.objects.filter(status='W', auct=auct).get()
            return render_to_response("auction.html", {'auct':auct, 'bb':b}, context_instance= RequestContext(request))

    else:
        mesg = _("You have to log in first")
        posts = auction.objects.all()
        return render_to_response("home.html", {'msg': mesg, 'posts': posts}, context_instance= RequestContext(request))

##################################################################################

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

#@csrf_exempt
def apisearch(request, tit=''):

    #if request.method == 'GET':
        #auctions = get_list_or_404(auction, title=tit)

    auctions = auction.objects.all().filter(title__contains=tit).exclude(lifecycle='B')
    if tit=='':
        auctions = auction.objects.all().exclude(lifecycle='B')
        serializer = AuctionSerializer(auctions, many=True)
        return JSONResponse(serializer.data)
        #return HttpResponse(status=400)

    elif len(auctions) < 1 and tit!='':
        return HttpResponseNotFound('<h1>Error 404\n</h1><h3>No auction found.</h3>', status=404)
        #return HttpResponse(status=404)
        #raise Http404

    else:
        serializer = AuctionSerializer(auctions, many=True)
        return JSONResponse(serializer.data)

    # this part is for use the search input in the templates, i only use it for try faster while developing
    # if request.method == 'POST':
    #     tit = request.POST.get('search', '')
    #     auctions = auction.objects.all().filter(title=tit)
    #     if len(auctions) < 1 and tit=='':
    #         auctions = auction.objects.all()
    #         serializer = AuctionSerializer(auction, many=True)
    #         return JSONResponse(serializer.data)
    #     elif len(auctions) < 1 and tit!='':
    #         return HttpResponseNotFound('<h1>Error 404\n</h1><h3>No auction found.</h3>', status=404)
    #     else:
    #         serializer = AuctionSerializer(auctions, many=True)
    #         return JSONResponse(serializer.data)

@csrf_exempt
def apibid(request, id):

    if request.user.is_authenticated():
        try:
            auct = auction.objects.get(id=id)
        except auction.DoesNotExist:
            return HttpResponseNotFound('<h1>Error 404\n</h1><h3>No auction found.</h3>', status=404)

        if request.method == 'POST':
            data = JSONParser().parse(request)
            serializer = BidSerializer(data=data)

            if serializer.is_valid():

                if auct.lock == True:
                    #auction locked by the seller
                    response_data = {}
                    response_data['result'] = 'Auction locked. You have to wait until the seller finish the edition.'
                    response_data['message'] = 'Error 404'
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                if auct.lifecycle != 'A':
                    #can't bid on this auction
                    #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>Auction not active.</h3>', status=404)
                    response_data = {}
                    response_data['result'] = 'Auction no active.'
                    response_data['message'] = 'Error 404'
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                if request.user == auct.seller:
                    #can't bid on this auction
                    #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>Can not bid on your own auction.</h3>', status=404)
                    response_data = {}
                    response_data['result'] = 'Can not bid on your own auction.'
                    response_data['message'] = 'Error 404'
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                if auct.min_price > float(data['amount'])  or (float(data['amount']) - auct.min_price < 0.01):
                    #bid have to be higher than min_price
                    #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>Amount have to be at least 0.01 bigger than minimum price.</h3>', status=404)
                    response_data = {}
                    response_data['result'] = 'Amount have to be at least 0.01 bigger than minimun price.'
                    response_data['message'] = 'Error 404'
                    return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                #this is the previous wining bid of the auction
                prev_bid_wining = bid.objects.filter(status='W', auct=auct)
                if prev_bid_wining:
                    prev_bid_wining = bid.objects.filter(status='W', auct=auct).get()

                #in case that exists
                if prev_bid_wining:

                    #can't bid because you are already wining this auction
                    if prev_bid_wining.user == request.user:
                        #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>You are already the winner of this auction.</h3>', status=404)
                        response_data = {}
                        response_data['result'] = 'You are already the winner of this auction.'
                        response_data['message'] = 'Error 404'
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                    #can't bid because previous bid is bigger that yours
                    if float(data['amount']) - prev_bid_wining.amount < 0.01:
                        #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>Bid has to be at less 0.01 bigger than previous bids.</h3>', status=404)
                        response_data = {}
                        response_data['result'] = 'Bid has to be at less 0.01 bigger than previous bids.'
                        response_data['message'] = 'Error 404'
                        return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

                    send_mail('Bid losing.', "Somebody bid in the same auction that you did.", 'no_repli@yaas.com', [prev_bid_wining.user.email,], fail_silently=False)
                    prev_bid_wining.status = 'L'
                    prev_bid_wining.save()


                b = bid(user=request.user, amount=data['amount'], auct=auct, status='W')
                b.save()

                #Optional feature: soft deadlines
                deadline = auct.deadline.strftime("%d/%m/%Y %H:%M:%S")
                d = datetime.datetime.strptime(deadline, "%d/%m/%Y %H:%M:%S")

                if (d - datetime.datetime.now()).total_seconds() < 350:
                    auct.deadline = auct.deadline + datetime.timedelta(seconds = 350)
                    auct.save()

                bb = model_to_dict(b)

                send_mail('New bid in your auction.', "Somebody bid in the one of your auctions.", 'no_repli@yaas.com', [auct.seller.email,], fail_silently=False)
                send_mail('Bid accepted.', "Your new bed has been acepted.", 'no_repli@yaas.com', [request.user.email,], fail_silently=False)

                return HttpResponse(json.dumps(bb), content_type='application/json')

            else:
                return JSONResponse(serializer.errors, status=400)

        else:
            #return HttpResponseNotFound('<h1>Error 404\n</h1><h3>No POST method.</h3>', status=404)
            #return JSONResponse(serializer.errors, status=400)
            response_data = {}
            response_data['result'] = 'No POST method'
            response_data['message'] = 'Error 404'
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)
    else:
        response_data = {}
        response_data['result'] = 'User no authenticated'
        response_data['message'] = 'Error 404'
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=404)

##################################################################################
