from datetime import date, timedelta
from unittest import TestCase

from django.test import RequestFactory
from mock import patch

from regulations.views import redirect


class ViewsRedirectTest(TestCase):
    @patch('regulations.views.redirect.ApiReader')
    def test_redirect_by_date(self, ApiReader):
        ApiReader.return_value.regversions.return_value = {'versions': [
            {'by_date': '2000-01-01', 'version': 'aaa'},
            {'by_date': '2005-05-05', 'version': 'bbb'},
            {'by_date': '2010-06-07', 'version': 'ccc'},
        ]}

        with patch('regulations.views.redirect.handle_generic_404') as handle:
            redirect.redirect_by_date(None, '8888', '1999', '10', '10')
            self.assertTrue(handle.called)

            handle.reset_mock()
            redirect.redirect_by_date(None, '8888', '', '', '')
            self.assertTrue(handle.called)

        response = redirect.redirect_by_date(None, '8888', '2000', '01', '01')
        self.assertEqual(302, response.status_code)
        self.assertTrue('aaa' in response['Location'])
        response = redirect.redirect_by_date(None, '8888', '2006', '06', '06')
        self.assertEqual(302, response.status_code)
        self.assertTrue('bbb' in response['Location'])
        response = redirect.redirect_by_date(None, '8888', '2010', '06', '08')
        self.assertEqual(302, response.status_code)
        self.assertTrue('ccc' in response['Location'])

    @patch('regulations.views.redirect.ApiReader')
    def test_redirect_by_current_date(self, ApiReader):
        today = date.today()
        last_week = (today - timedelta(7)).isoformat()
        next_week = (today + timedelta(7)).isoformat()
        ApiReader.return_value.regversions.return_value = {'versions': [
            {'by_date': last_week, 'version': 'last_week'},
            {'by_date': today.isoformat(), 'version': 'today'},
            {'by_date': next_week, 'version': 'next_week'},
        ]}

        response = redirect.redirect_by_current_date(None, '8888')
        self.assertEqual(302, response.status_code)
        self.assertTrue('today' in response['Location'])

    @patch('regulations.views.redirect.redirect_by_date')
    def test_redirect_by_date_get(self, redirect_by_date):
        request = RequestFactory().get('?year=2222&month=11&day=20')
        redirect.redirect_by_date_get(request, 'lablab')
        self.assertTrue(redirect_by_date.called)
        self.assertEqual(('lablab', '2222', '11', '20'),
                         redirect_by_date.call_args[0][1:])

        request = RequestFactory().get('?year=-2222&month=-11&day=-20')
        redirect.redirect_by_date_get(request, 'lablab')
        self.assertTrue(redirect_by_date.called)
        self.assertEqual(('lablab', '2222', '11', '20'),
                         redirect_by_date.call_args[0][1:])

        request = RequestFactory().get('?year=123&month=1&day=2')
        redirect_by_date.reset_mock()
        redirect.redirect_by_date_get(request, 'lablab')
        self.assertTrue(redirect_by_date.called)
        self.assertEqual(('lablab', '0123', '01', '02'),
                         redirect_by_date.call_args[0][1:])

        request = RequestFactory().get('?year=22&month=1&day=2')
        redirect_by_date.reset_mock()
        redirect.redirect_by_date_get(request, 'lablab')
        self.assertTrue(redirect_by_date.called)
        self.assertEqual(('lablab', '2022', '01', '02'),
                         redirect_by_date.call_args[0][1:])

        with patch('regulations.views.redirect.handle_generic_404') as handle:
            request = RequestFactory().get('?year=bad&month=data&day=here')
            redirect.redirect_by_date_get(request, 'lablab')
            self.assertTrue(handle.called)

        with patch('regulations.views.redirect.handle_generic_404') as handle:
            request = RequestFactory().get('')
            redirect.redirect_by_date_get(request, 'lablab')
            self.assertTrue(handle.called)

            handle.reset_mock()
            request = RequestFactory().get('?year=2222')
            redirect.redirect_by_date_get(request, 'lablab')
            self.assertTrue(handle.called)

    def test_diff_redirect_bad_version(self):
        request = RequestFactory().get('?new_version=A+Bad+Version')
        response = redirect.diff_redirect(request, 'lablab', 'verver')
        self.assertEqual(404, response.status_code)

    @patch('regulations.views.redirect.fetch_grouped_history')
    def test_diff_redirect_order(self, fgh):
        fgh.return_value = [
            {'notices': [{'document_number': '3'}, {'document_number': '2'}]},
            {'notices': [{'document_number': '1'}]}]
        request = RequestFactory().get('?new_version=3')
        response = redirect.diff_redirect(request, '1111-22', '1')
        self.assertTrue('diff/1111-22/1/3' in response['Location'])
        self.assertTrue('from_version=1' in response['Location'])
        response = redirect.diff_redirect(request, '1111-22', '2')
        self.assertTrue('diff/1111-22/2/3' in response['Location'])
        self.assertTrue('from_version=2' in response['Location'])

        request = RequestFactory().get('?new_version=2')
        response = redirect.diff_redirect(request, '1111-22', '1')
        self.assertTrue('diff/1111-22/1/2' in response['Location'])
        self.assertTrue('from_version=1' in response['Location'])
        response = redirect.diff_redirect(request, '1111-22', '3')
        self.assertTrue('diff/1111-22/2/3' in response['Location'])
        self.assertTrue('from_version=3' in response['Location'])

        request = RequestFactory().get('?new_version=1')
        response = redirect.diff_redirect(request, '1111-22', '2')
        self.assertTrue('diff/1111-22/1/2' in response['Location'])
        self.assertTrue('from_version=2' in response['Location'])
        response = redirect.diff_redirect(request, '1111-22', '3')
        self.assertTrue('diff/1111-22/1/3' in response['Location'])
        self.assertTrue('from_version=3' in response['Location'])
