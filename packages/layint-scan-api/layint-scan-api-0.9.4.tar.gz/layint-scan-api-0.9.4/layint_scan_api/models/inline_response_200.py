# coding: utf-8

"""
    Layered Insight Scan

    Layered Insight Scan performs static vulnerability analysis, license and package compliance.  You can find out more about Scan at http://layeredinsight.com.

    OpenAPI spec version: 0.9.4
    Contact: help@layeredinsight.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class InlineResponse200(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'name': 'str',
        'version': 'str',
        'license': 'str'
    }

    attribute_map = {
        'name': 'Name',
        'version': 'Version',
        'license': 'License'
    }

    def __init__(self, name=None, version=None, license=None):
        """
        InlineResponse200 - a model defined in Swagger
        """

        self._name = None
        self._version = None
        self._license = None

        if name is not None:
          self.name = name
        if version is not None:
          self.version = version
        if license is not None:
          self.license = license

    @property
    def name(self):
        """
        Gets the name of this InlineResponse200.

        :return: The name of this InlineResponse200.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this InlineResponse200.

        :param name: The name of this InlineResponse200.
        :type: str
        """

        self._name = name

    @property
    def version(self):
        """
        Gets the version of this InlineResponse200.

        :return: The version of this InlineResponse200.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this InlineResponse200.

        :param version: The version of this InlineResponse200.
        :type: str
        """

        self._version = version

    @property
    def license(self):
        """
        Gets the license of this InlineResponse200.

        :return: The license of this InlineResponse200.
        :rtype: str
        """
        return self._license

    @license.setter
    def license(self, license):
        """
        Sets the license of this InlineResponse200.

        :param license: The license of this InlineResponse200.
        :type: str
        """

        self._license = license

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, InlineResponse200):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
