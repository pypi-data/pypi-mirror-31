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


class ClairFeature(object):
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
        'namespace_name': 'str',
        'version': 'str',
        'added_by': 'str',
        'vulnerabilities': 'list[ClairVulnerability]'
    }

    attribute_map = {
        'name': 'Name',
        'namespace_name': 'NamespaceName',
        'version': 'Version',
        'added_by': 'AddedBy',
        'vulnerabilities': 'Vulnerabilities'
    }

    def __init__(self, name=None, namespace_name=None, version=None, added_by=None, vulnerabilities=None):
        """
        ClairFeature - a model defined in Swagger
        """

        self._name = None
        self._namespace_name = None
        self._version = None
        self._added_by = None
        self._vulnerabilities = None

        if name is not None:
          self.name = name
        if namespace_name is not None:
          self.namespace_name = namespace_name
        if version is not None:
          self.version = version
        if added_by is not None:
          self.added_by = added_by
        if vulnerabilities is not None:
          self.vulnerabilities = vulnerabilities

    @property
    def name(self):
        """
        Gets the name of this ClairFeature.
        Name of the feature (usually package name)

        :return: The name of this ClairFeature.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this ClairFeature.
        Name of the feature (usually package name)

        :param name: The name of this ClairFeature.
        :type: str
        """

        self._name = name

    @property
    def namespace_name(self):
        """
        Gets the namespace_name of this ClairFeature.
        Name of the namespace (eg os distribution)

        :return: The namespace_name of this ClairFeature.
        :rtype: str
        """
        return self._namespace_name

    @namespace_name.setter
    def namespace_name(self, namespace_name):
        """
        Sets the namespace_name of this ClairFeature.
        Name of the namespace (eg os distribution)

        :param namespace_name: The namespace_name of this ClairFeature.
        :type: str
        """

        self._namespace_name = namespace_name

    @property
    def version(self):
        """
        Gets the version of this ClairFeature.
        Version of the feature

        :return: The version of this ClairFeature.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this ClairFeature.
        Version of the feature

        :param version: The version of this ClairFeature.
        :type: str
        """

        self._version = version

    @property
    def added_by(self):
        """
        Gets the added_by of this ClairFeature.
        Refers to container image that this was found in

        :return: The added_by of this ClairFeature.
        :rtype: str
        """
        return self._added_by

    @added_by.setter
    def added_by(self, added_by):
        """
        Sets the added_by of this ClairFeature.
        Refers to container image that this was found in

        :param added_by: The added_by of this ClairFeature.
        :type: str
        """

        self._added_by = added_by

    @property
    def vulnerabilities(self):
        """
        Gets the vulnerabilities of this ClairFeature.

        :return: The vulnerabilities of this ClairFeature.
        :rtype: list[ClairVulnerability]
        """
        return self._vulnerabilities

    @vulnerabilities.setter
    def vulnerabilities(self, vulnerabilities):
        """
        Sets the vulnerabilities of this ClairFeature.

        :param vulnerabilities: The vulnerabilities of this ClairFeature.
        :type: list[ClairVulnerability]
        """

        self._vulnerabilities = vulnerabilities

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
        if not isinstance(other, ClairFeature):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
