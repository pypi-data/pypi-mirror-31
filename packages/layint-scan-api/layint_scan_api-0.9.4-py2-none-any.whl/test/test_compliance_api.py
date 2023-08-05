# coding: utf-8

"""
    Layered Insight Scan

    Layered Insight Scan performs static vulnerability analysis, license and package compliance.  You can find out more about Scan at http://layeredinsight.com.

    OpenAPI spec version: 0.9.4
    Contact: help@layeredinsight.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import os
import sys
import unittest

import layint_scan_api
from layint_scan_api.rest import ApiException
from layint_scan_api.apis.compliance_api import ComplianceApi


class TestComplianceApi(unittest.TestCase):
    """ ComplianceApi unit test stubs """

    def setUp(self):
        self.api = layint_scan_api.apis.compliance_api.ComplianceApi()

    def tearDown(self):
        pass

    def test_add_policy(self):
        """
        Test case for add_policy

        Add a new policy
        """
        pass

    def test_add_policy_rule(self):
        """
        Test case for add_policy_rule

        Add a new policy rule
        """
        pass

    def test_delete_policy(self):
        """
        Test case for delete_policy

        Delete compliance policy
        """
        pass

    def test_delete_policy_rule(self):
        """
        Test case for delete_policy_rule

        Delete compliance policy rule
        """
        pass

    def test_get_policies(self):
        """
        Test case for get_policies

        List all compliance policies available to the user
        """
        pass

    def test_get_policy(self):
        """
        Test case for get_policy

        Get compliance policy
        """
        pass

    def test_get_policy_rule(self):
        """
        Test case for get_policy_rule

        Get compliance policy rule
        """
        pass

    def test_get_policy_rules(self):
        """
        Test case for get_policy_rules

        List all compliance rules available to the user
        """
        pass

    def test_update_policy(self):
        """
        Test case for update_policy

        Update policy
        """
        pass

    def test_update_policy_rule(self):
        """
        Test case for update_policy_rule

        Update policy rule
        """
        pass


if __name__ == '__main__':
    unittest.main()
