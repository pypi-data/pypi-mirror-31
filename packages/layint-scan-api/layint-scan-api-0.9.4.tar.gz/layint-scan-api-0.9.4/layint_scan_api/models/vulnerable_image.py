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


class VulnerableImage(object):
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
        'image': 'str',
        'score': 'float'
    }

    attribute_map = {
        'image': 'Image',
        'score': 'Score'
    }

    def __init__(self, image=None, score=None):
        """
        VulnerableImage - a model defined in Swagger
        """

        self._image = None
        self._score = None

        if image is not None:
          self.image = image
        if score is not None:
          self.score = score

    @property
    def image(self):
        """
        Gets the image of this VulnerableImage.
        Name of vulnerable image

        :return: The image of this VulnerableImage.
        :rtype: str
        """
        return self._image

    @image.setter
    def image(self, image):
        """
        Sets the image of this VulnerableImage.
        Name of vulnerable image

        :param image: The image of this VulnerableImage.
        :type: str
        """

        self._image = image

    @property
    def score(self):
        """
        Gets the score of this VulnerableImage.
        Score of vulnerable image

        :return: The score of this VulnerableImage.
        :rtype: float
        """
        return self._score

    @score.setter
    def score(self, score):
        """
        Sets the score of this VulnerableImage.
        Score of vulnerable image

        :param score: The score of this VulnerableImage.
        :type: float
        """

        self._score = score

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
        if not isinstance(other, VulnerableImage):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
