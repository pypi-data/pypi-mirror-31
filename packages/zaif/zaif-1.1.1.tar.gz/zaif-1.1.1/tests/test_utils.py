# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from zaif import utils
from time import sleep


class TestUtils(unittest2.TestCase):
    def test_method_name_returns_current_active_function_name(self):
        def mock_function(*args,**kwargs):
            self.assertEqual(utils.method_name(),'mock_function')


    def test_http_uri_issues_uri_security_warning(self):
        http_uri = 'http://foo.bar/baz'
        with self.assertWarns(UserWarning):
            utils.check_uri_security(http_uri)

    def test_get_nonce_returns_unique_values(self):
        nonce1 = utils.get_nonce()
        sleep(1)
        nonce2 =  utils.get_nonce()
        self.assertNotEqual(nonce1,nonce2)
        
