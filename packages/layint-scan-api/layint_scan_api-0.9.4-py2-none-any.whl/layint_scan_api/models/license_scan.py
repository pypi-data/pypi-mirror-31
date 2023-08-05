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


class LicenseScan(object):
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
        'expire': 'str',
        'max_scanned_images': 'int',
        'max_scans_per_month': 'int',
        'options': 'object'
    }

    attribute_map = {
        'expire': 'Expire',
        'max_scanned_images': 'MaxScannedImages',
        'max_scans_per_month': 'MaxScansPerMonth',
        'options': 'Options'
    }

    def __init__(self, expire=None, max_scanned_images=None, max_scans_per_month=None, options=None):
        """
        LicenseScan - a model defined in Swagger
        """

        self._expire = None
        self._max_scanned_images = None
        self._max_scans_per_month = None
        self._options = None

        if expire is not None:
          self.expire = expire
        if max_scanned_images is not None:
          self.max_scanned_images = max_scanned_images
        if max_scans_per_month is not None:
          self.max_scans_per_month = max_scans_per_month
        if options is not None:
          self.options = options

    @property
    def expire(self):
        """
        Gets the expire of this LicenseScan.
        Expiration date/time for scan

        :return: The expire of this LicenseScan.
        :rtype: str
        """
        return self._expire

    @expire.setter
    def expire(self, expire):
        """
        Sets the expire of this LicenseScan.
        Expiration date/time for scan

        :param expire: The expire of this LicenseScan.
        :type: str
        """

        self._expire = expire

    @property
    def max_scanned_images(self):
        """
        Gets the max_scanned_images of this LicenseScan.
        Maximum number of allowed scanned images to be stored

        :return: The max_scanned_images of this LicenseScan.
        :rtype: int
        """
        return self._max_scanned_images

    @max_scanned_images.setter
    def max_scanned_images(self, max_scanned_images):
        """
        Sets the max_scanned_images of this LicenseScan.
        Maximum number of allowed scanned images to be stored

        :param max_scanned_images: The max_scanned_images of this LicenseScan.
        :type: int
        """

        self._max_scanned_images = max_scanned_images

    @property
    def max_scans_per_month(self):
        """
        Gets the max_scans_per_month of this LicenseScan.
        Maximum number of allowed scans to be run per month

        :return: The max_scans_per_month of this LicenseScan.
        :rtype: int
        """
        return self._max_scans_per_month

    @max_scans_per_month.setter
    def max_scans_per_month(self, max_scans_per_month):
        """
        Sets the max_scans_per_month of this LicenseScan.
        Maximum number of allowed scans to be run per month

        :param max_scans_per_month: The max_scans_per_month of this LicenseScan.
        :type: int
        """

        self._max_scans_per_month = max_scans_per_month

    @property
    def options(self):
        """
        Gets the options of this LicenseScan.
        Options

        :return: The options of this LicenseScan.
        :rtype: object
        """
        return self._options

    @options.setter
    def options(self, options):
        """
        Sets the options of this LicenseScan.
        Options

        :param options: The options of this LicenseScan.
        :type: object
        """

        self._options = options

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
        if not isinstance(other, LicenseScan):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
