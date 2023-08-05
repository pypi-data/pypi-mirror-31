import simplejson as json
from decimal import Decimal
import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock
from requests import HTTPError

from . import PaypalProvider, PaypalCardProvider
from web_payments import RedirectNeeded, PaymentError, PaymentStatus
from web_payments.testcommon import create_test_payment

CLIENT_ID = 'abc123'
PAYMENT_TOKEN = '5a4dae68-2715-4b1e-8bb2-2c2dbe9255f6'
SECRET = '123abc'
VARIANT = 'paypal'

PROCESS_DATA = {
    'name': 'John Doe',
    'number': '371449635398431',
    'expiration': (datetime.datetime.now()+datetime.timedelta(weeks=3*52)).strftime("%m/%Y"),
    'cvv2': '1234'}

Payment = create_test_payment(variant=VARIANT, token=PAYMENT_TOKEN)
Payment.extra_data = json.dumps({'links': {
        'approval_url': None,
        'capture': {'href': 'http://capture.com'},
        'refund': {'href': 'http://refund.com'},
        'execute': {'href': 'http://execute.com'}
    }})


class TestPaypalProvider(TestCase):

    def setUp(self):
        self.payment = Payment()
        self.provider = PaypalProvider(secret=SECRET, client_id=CLIENT_ID)

    def test_provider_raises_redirect_needed_on_success(self):
        with patch('requests.post') as mocked_post:
            transaction_id = '1234'
            data = MagicMock()
            data.return_value = {
                'id': transaction_id,
                'token_type': 'test_token_type',
                'access_token': 'test_access_token',
                'links': [
                    {'rel': 'approval_url', 'href': 'http://approval_url.com'}
                ]}
            post = MagicMock()
            post.json = data
            post.status_code = 200
            mocked_post.return_value = post
            with self.assertRaises(RedirectNeeded) as cm:
                self.provider.get_form(payment=self.payment)
        self.assertEqual(self.payment.status, PaymentStatus.WAITING)
        self.assertEqual(self.payment.captured_amount, Decimal('0'))
        self.assertEqual(self.payment.transaction_id, transaction_id)

    @patch('requests.post')
    def test_provider_captures_payment(self, mocked_post):
        data = MagicMock()
        data.return_value = {
            'state': 'completed',
            'token_type': 'test_token_type',
            'access_token': 'test_access_token'}
        post = MagicMock()
        post.json = data
        post.status_code = 200
        mocked_post.return_value = post
        self.provider.capture(self.payment)
        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)

    @patch('requests.post')
    def test_provider_handles_captured_payment(self, mocked_post):
        data = MagicMock()
        data.return_value = {
            'name': 'AUTHORIZATION_ALREADY_COMPLETED'}
        response = MagicMock()
        response.json = data
        mocked_post.side_effect = HTTPError(response=response)
        self.provider.capture(self.payment)
        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)

    @patch('requests.post')
    def test_provider_refunds_payment(self, mocked_post):
        data = MagicMock()
        data.return_value = {
            'token_type': 'test_token_type',
            'access_token': 'test_access_token'}
        post = MagicMock()
        post.json = data
        post.status_code = 200
        mocked_post.return_value = post
        self.provider.refund(self.payment)
        self.assertEqual(self.payment.status, PaymentStatus.REFUNDED)

    @patch('requests.post')
    def test_provider_redirects_on_success_captured_payment(
            self, mocked_post):
        data = MagicMock()
        data.return_value = {
            'token_type': 'test_token_type',
            'access_token': 'test_access_token',
            'payer': {'payer_info': 'test123'},
            'transactions': [
                {'related_resources': [{
                    'sale': {'links': ''},
                    'authorization': {'links': ''}}]}
            ]}
        post = MagicMock()
        post.json = data
        post.status_code = 200
        mocked_post.return_value = post

        request = MagicMock()
        request.GET = {'token': 'test', 'PayerID': '1234'}
        with self.assertRaises(RedirectNeeded) as cm:
            self.provider.process_data(self.payment, request)

        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)
        self.assertEqual(self.payment.captured_amount, self.payment.total)

    @patch('requests.post')
    def test_provider_redirects_on_success_preauth_payment(
            self, mocked_post):
        data = MagicMock()
        data.return_value = {
            'token_type': 'test_token_type',
            'access_token': 'test_access_token',
            'payer': {'payer_info': 'test123'},
            'transactions': [
                {'related_resources': [{
                    'sale': {'links': ''},
                    'authorization': {'links': ''}}]}
            ]}
        post = MagicMock()
        post.json = data
        post.status_code = 200
        mocked_post.return_value = post

        request = MagicMock()
        request.GET = {'token': 'test', 'PayerID': '1234'}
        provider = PaypalProvider(
            secret=SECRET, client_id=CLIENT_ID, capture=False)
        with self.assertRaises(RedirectNeeded) as cm:
            provider.process_data(self.payment, request)

        self.assertEqual(self.payment.status, PaymentStatus.PREAUTH)
        self.assertEqual(self.payment.captured_amount, Decimal('0'))

    def test_provider_request_without_payerid_redirects_on_failure(
            self):
        request = MagicMock()
        request.GET = {'token': 'test', 'PayerID': None}
        with self.assertRaises(RedirectNeeded) as cm:
            self.provider.process_data(self.payment, request)
        self.assertEqual(self.payment.status, PaymentStatus.REJECTED)

    @patch('requests.post')
    def test_provider_renews_access_token(self, mocked_post):
        new_token = 'new_test_token'
        response401 = MagicMock()
        response401.status_code = 401
        data = MagicMock()
        data.return_value = {'access_token': new_token, 'token_type': 'test_token_type'}
        response = MagicMock()
        response.json = data
        response.response_type = "application/json"
        response.status_code = 200
        mocked_post.side_effect = [
            HTTPError(response=response401), response, response]

        self.payment.extra_data = json.dumps({
            'auth_response': {
                'access_token': 'expired_token',
                'token_type': 'token type',
                'expires_in': 99999}})
        self.provider.post(self.payment, self.provider.payments_url, data=self.provider.get_product_data(self.payment))
        self.assertEqual(self.provider.token_cache.token, "test_token_type %s" % new_token)


class TestPaypalCardProvider(TestCase):

    def setUp(self):
        self.payment = Payment(extra_data='')
        self.provider = PaypalCardProvider(secret=SECRET, client_id=CLIENT_ID)

    def test_provider_raises_redirect_needed_on_success_captured_payment(self):
        with patch('requests.post') as mocked_post:
            transaction_id = '1234'
            data = MagicMock()
            data.return_value = {
                'id': transaction_id,
                'token_type': 'test_token_type',
                'access_token': 'test_access_token',
                'transactions': [
                    {'related_resources': [
                        {'sale': {'links': [
                            {'rel': 'refund', 'href': 'http://refund.com'}]}}
                    ]}
                ]}
            post = MagicMock()
            post.json = data
            post.status_code = 200
            mocked_post.return_value = post
            with self.assertRaises(RedirectNeeded) as exc:
                self.provider.get_form(
                    payment=self.payment, data=PROCESS_DATA)
                self.assertEqual(exc.args[0], self.payment.get_success_url())
        links = self.payment.attrs.links
        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)
        self.assertEqual(self.payment.captured_amount, self.payment.total)
        self.assertEqual(self.payment.transaction_id, transaction_id)
        self.assertTrue('refund' in links)

    def test_provider_raises_redirect_needed_on_success_preauth_payment(self):
        provider = PaypalCardProvider(
            secret=SECRET, client_id=CLIENT_ID, capture=False)
        with patch('requests.post') as mocked_post:
            transaction_id = '1234'
            data = MagicMock()
            data.return_value = {
                'id': transaction_id,
                'token_type': 'test_token_type',
                'access_token': 'test_access_token',
                'transactions': [
                    {'related_resources': [
                        {'authorization': {'links': [
                            {'rel': 'refund', 'href': 'http://refund.com'},
                            {'rel': 'capture', 'href': 'http://capture.com'}]}}
                    ]}
                ]}
            post = MagicMock()
            post.json = data
            post.status_code = 200
            mocked_post.return_value = post
            with self.assertRaises(RedirectNeeded) as exc:
                provider.get_form(
                    payment=self.payment, data=PROCESS_DATA)
                self.assertEqual(exc.args[0], self.payment.get_success_url())
        links = self.payment.attrs.links
        self.assertEqual(self.payment.status, PaymentStatus.PREAUTH)
        self.assertEqual(self.payment.captured_amount, Decimal('0'))
        self.assertEqual(self.payment.transaction_id, transaction_id)
        self.assertTrue('capture' in links)
        self.assertTrue('refund' in links)

    def test_form_error_message(self):
        with patch('requests.post') as mocked_post:
            error_message = 'error message'
            data = MagicMock()
            data.return_value = {'details': [{'issue': error_message}]}
            post = MagicMock()
            post.json = data
            post.status_code = 400
            mocked_post.side_effect = HTTPError(response=post)
            with self.assertRaises(PaymentError) as exc:
                form = self.provider.get_form(
                    payment=self.payment, data=PROCESS_DATA)

        self.assertEqual(self.payment.status, PaymentStatus.ERROR)

    def test_form_internal_error_message(self):
        with patch('requests.post') as mocked_post:
            error_message = 'error message'
            data = MagicMock()
            data.return_value = {
                'token_type': 'test_token_type',
                'access_token': 'test_access_token',
                'message': error_message}
            post = MagicMock()
            post.status_code = 400
            post.json = data
            mocked_post.return_value = post
            with self.assertRaises(PaymentError) as exc:
                self.provider.get_form(
                    payment=self.payment, data=PROCESS_DATA)
        self.assertEqual(self.payment.status, PaymentStatus.ERROR)
        self.assertEqual(self.payment.message, error_message)
