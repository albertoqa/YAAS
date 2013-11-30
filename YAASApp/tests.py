from django.test import TestCase
from YAASApp.models import *
from YAASApp.forms import *

class SimpleTest(TestCase):
    fixtures = ['initial_data.json']

    # test of the form
    def test_form(self):
        form_data = {'title': 'something', 'description': 'something2', 'min_price': '10.0', 'deadline': '01/01/2014 01:01'}
        form = createAuction(data=form_data)
        self.assertEqual(form.is_valid(), True)

        # i write a grown deadline
        form_data = {'title': 'something', 'description': 'something2', 'min_price': '10.0', 'deadline': '01/111/2014 01:01'}
        form = createAuction(data=form_data)
        self.assertEqual(form.is_valid(), False)

    # test of add auction
    def test_add_auction(self):

        self.user = User.objects.create(username='test', password='test')
        self.user.set_password('test')
        self.user.save()
        self.client.login(username='test', password='test')

        #test 1
        # if form is not valid error in line 28
        response = self.client.post('/addauction/',{'title':'qwerty','description':'zxcvb','min_price':'10','deadline':'01/01/2014 01:01'})
        self.failUnlessEqual(response.status_code,200)
        self.assertContains(response, "Confirm")
        response = self.client.post('/saveauction/', {'option':'Yes', 'title':'qwerty','description':'zxcvb','min_price':'10','deadline':'01/01/2014 01:01:01'})
        self.failUnlessEqual(response.status_code,200)
        self.assertContains(response, "Thanks.")

        response = self.client.post('/saveauction/', {'option':'No', 'title':'qwerty','description':'zxcvb','min_price':'10','deadline':'01/01/2014 01:01:01'})
        self.failUnlessEqual(response.status_code,200)
        self.assertContains(response, "not saved")

        #test 3
        self.client.logout()
        response = self.client.post('/addauction/',{'title':'qwerty','description':'zxcvb','min_price':'10','deadline':'01/01/2014 01:01'})
        self.failUnlessEqual(response.status_code,200)
        self.assertContains(response, "You have to log in")
        response = self.client.post('/saveauction/', {'option':'No', 'title':'qwerty','description':'zxcvb','min_price':'10','deadline':'01/01/2014 01:01:01'})
        self.failUnlessEqual(response.status_code,200)
        self.assertContains(response, "You have to log in")

