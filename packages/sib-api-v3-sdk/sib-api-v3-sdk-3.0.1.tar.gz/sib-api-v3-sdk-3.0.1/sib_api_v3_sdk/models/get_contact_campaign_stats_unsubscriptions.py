# coding: utf-8

"""
    SendinBlue API

    SendinBlue provide a RESTFul API that can be used with any languages. With this API, you will be able to :   - Manage your campaigns and get the statistics   - Manage your contacts   - Send transactional Emails and SMS   - and much more...  You can download our wrappers at https://github.com/orgs/sendinblue  **Possible responses**   | Code | Message |   | :-------------: | ------------- |   | 200  | OK. Successful Request  |   | 201  | OK. Successful Creation |   | 202  | OK. Request accepted |   | 204  | OK. Successful Update/Deletion  |   | 400  | Error. Bad Request  |   | 401  | Error. Authentication Needed  |   | 402  | Error. Not enough credit, plan upgrade needed  |   | 403  | Error. Permission denied  |   | 404  | Error. Object does not exist |   | 405  | Error. Method not allowed  |   # noqa: E501

    OpenAPI spec version: 3.0.0
    Contact: contact@sendinblue.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from sib_api_v3_sdk.models.get_extended_contact_details_statistics_unsubscriptions_admin_unsubscription import GetExtendedContactDetailsStatisticsUnsubscriptionsAdminUnsubscription  # noqa: F401,E501
from sib_api_v3_sdk.models.get_extended_contact_details_statistics_unsubscriptions_user_unsubscription import GetExtendedContactDetailsStatisticsUnsubscriptionsUserUnsubscription  # noqa: F401,E501


class GetContactCampaignStatsUnsubscriptions(object):
    """NOTE: This class is auto generated by the swagger code generator program.

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
        'user_unsubscription': 'list[GetExtendedContactDetailsStatisticsUnsubscriptionsUserUnsubscription]',
        'admin_unsubscription': 'list[GetExtendedContactDetailsStatisticsUnsubscriptionsAdminUnsubscription]'
    }

    attribute_map = {
        'user_unsubscription': 'userUnsubscription',
        'admin_unsubscription': 'adminUnsubscription'
    }

    def __init__(self, user_unsubscription=None, admin_unsubscription=None):  # noqa: E501
        """GetContactCampaignStatsUnsubscriptions - a model defined in Swagger"""  # noqa: E501

        self._user_unsubscription = None
        self._admin_unsubscription = None
        self.discriminator = None

        self.user_unsubscription = user_unsubscription
        self.admin_unsubscription = admin_unsubscription

    @property
    def user_unsubscription(self):
        """Gets the user_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501

        Contact has unsubscribed via the unsubscription link in the email  # noqa: E501

        :return: The user_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501
        :rtype: list[GetExtendedContactDetailsStatisticsUnsubscriptionsUserUnsubscription]
        """
        return self._user_unsubscription

    @user_unsubscription.setter
    def user_unsubscription(self, user_unsubscription):
        """Sets the user_unsubscription of this GetContactCampaignStatsUnsubscriptions.

        Contact has unsubscribed via the unsubscription link in the email  # noqa: E501

        :param user_unsubscription: The user_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501
        :type: list[GetExtendedContactDetailsStatisticsUnsubscriptionsUserUnsubscription]
        """
        if user_unsubscription is None:
            raise ValueError("Invalid value for `user_unsubscription`, must not be `None`")  # noqa: E501

        self._user_unsubscription = user_unsubscription

    @property
    def admin_unsubscription(self):
        """Gets the admin_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501

        Contact has been unsubscribed from the administrator  # noqa: E501

        :return: The admin_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501
        :rtype: list[GetExtendedContactDetailsStatisticsUnsubscriptionsAdminUnsubscription]
        """
        return self._admin_unsubscription

    @admin_unsubscription.setter
    def admin_unsubscription(self, admin_unsubscription):
        """Sets the admin_unsubscription of this GetContactCampaignStatsUnsubscriptions.

        Contact has been unsubscribed from the administrator  # noqa: E501

        :param admin_unsubscription: The admin_unsubscription of this GetContactCampaignStatsUnsubscriptions.  # noqa: E501
        :type: list[GetExtendedContactDetailsStatisticsUnsubscriptionsAdminUnsubscription]
        """
        if admin_unsubscription is None:
            raise ValueError("Invalid value for `admin_unsubscription`, must not be `None`")  # noqa: E501

        self._admin_unsubscription = admin_unsubscription

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, GetContactCampaignStatsUnsubscriptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
