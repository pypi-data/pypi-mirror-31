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

from sib_api_v3_sdk.models.send_smtp_email_attachment import SendSmtpEmailAttachment  # noqa: F401,E501
from sib_api_v3_sdk.models.send_smtp_email_bcc import SendSmtpEmailBcc  # noqa: F401,E501
from sib_api_v3_sdk.models.send_smtp_email_cc import SendSmtpEmailCc  # noqa: F401,E501
from sib_api_v3_sdk.models.send_smtp_email_reply_to import SendSmtpEmailReplyTo  # noqa: F401,E501
from sib_api_v3_sdk.models.send_smtp_email_sender import SendSmtpEmailSender  # noqa: F401,E501
from sib_api_v3_sdk.models.send_smtp_email_to import SendSmtpEmailTo  # noqa: F401,E501


class SendSmtpEmail(object):
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
        'sender': 'SendSmtpEmailSender',
        'to': 'list[SendSmtpEmailTo]',
        'bcc': 'list[SendSmtpEmailBcc]',
        'cc': 'list[SendSmtpEmailCc]',
        'html_content': 'str',
        'text_content': 'str',
        'subject': 'str',
        'reply_to': 'SendSmtpEmailReplyTo',
        'attachment': 'list[SendSmtpEmailAttachment]',
        'headers': 'dict(str, str)',
        'template_id': 'int',
        'params': 'dict(str, str)'
    }

    attribute_map = {
        'sender': 'sender',
        'to': 'to',
        'bcc': 'bcc',
        'cc': 'cc',
        'html_content': 'htmlContent',
        'text_content': 'textContent',
        'subject': 'subject',
        'reply_to': 'replyTo',
        'attachment': 'attachment',
        'headers': 'headers',
        'template_id': 'templateId',
        'params': 'params'
    }

    def __init__(self, sender=None, to=None, bcc=None, cc=None, html_content=None, text_content=None, subject=None, reply_to=None, attachment=None, headers=None, template_id=None, params=None):  # noqa: E501
        """SendSmtpEmail - a model defined in Swagger"""  # noqa: E501

        self._sender = None
        self._to = None
        self._bcc = None
        self._cc = None
        self._html_content = None
        self._text_content = None
        self._subject = None
        self._reply_to = None
        self._attachment = None
        self._headers = None
        self._template_id = None
        self._params = None
        self.discriminator = None

        if sender is not None:
            self.sender = sender
        self.to = to
        if bcc is not None:
            self.bcc = bcc
        if cc is not None:
            self.cc = cc
        if html_content is not None:
            self.html_content = html_content
        if text_content is not None:
            self.text_content = text_content
        if subject is not None:
            self.subject = subject
        if reply_to is not None:
            self.reply_to = reply_to
        if attachment is not None:
            self.attachment = attachment
        if headers is not None:
            self.headers = headers
        if template_id is not None:
            self.template_id = template_id
        if params is not None:
            self.params = params

    @property
    def sender(self):
        """Gets the sender of this SendSmtpEmail.  # noqa: E501


        :return: The sender of this SendSmtpEmail.  # noqa: E501
        :rtype: SendSmtpEmailSender
        """
        return self._sender

    @sender.setter
    def sender(self, sender):
        """Sets the sender of this SendSmtpEmail.


        :param sender: The sender of this SendSmtpEmail.  # noqa: E501
        :type: SendSmtpEmailSender
        """

        self._sender = sender

    @property
    def to(self):
        """Gets the to of this SendSmtpEmail.  # noqa: E501

        Email addresses and names of the recipients  # noqa: E501

        :return: The to of this SendSmtpEmail.  # noqa: E501
        :rtype: list[SendSmtpEmailTo]
        """
        return self._to

    @to.setter
    def to(self, to):
        """Sets the to of this SendSmtpEmail.

        Email addresses and names of the recipients  # noqa: E501

        :param to: The to of this SendSmtpEmail.  # noqa: E501
        :type: list[SendSmtpEmailTo]
        """
        if to is None:
            raise ValueError("Invalid value for `to`, must not be `None`")  # noqa: E501

        self._to = to

    @property
    def bcc(self):
        """Gets the bcc of this SendSmtpEmail.  # noqa: E501

        Email addresses and names of the recipients in bcc  # noqa: E501

        :return: The bcc of this SendSmtpEmail.  # noqa: E501
        :rtype: list[SendSmtpEmailBcc]
        """
        return self._bcc

    @bcc.setter
    def bcc(self, bcc):
        """Sets the bcc of this SendSmtpEmail.

        Email addresses and names of the recipients in bcc  # noqa: E501

        :param bcc: The bcc of this SendSmtpEmail.  # noqa: E501
        :type: list[SendSmtpEmailBcc]
        """

        self._bcc = bcc

    @property
    def cc(self):
        """Gets the cc of this SendSmtpEmail.  # noqa: E501

        Email addresses and names of the recipients in cc  # noqa: E501

        :return: The cc of this SendSmtpEmail.  # noqa: E501
        :rtype: list[SendSmtpEmailCc]
        """
        return self._cc

    @cc.setter
    def cc(self, cc):
        """Sets the cc of this SendSmtpEmail.

        Email addresses and names of the recipients in cc  # noqa: E501

        :param cc: The cc of this SendSmtpEmail.  # noqa: E501
        :type: list[SendSmtpEmailCc]
        """

        self._cc = cc

    @property
    def html_content(self):
        """Gets the html_content of this SendSmtpEmail.  # noqa: E501

        HTML body of the message ( Mandatory if 'templateId' is not passed, ignored if 'templateId' is passed )  # noqa: E501

        :return: The html_content of this SendSmtpEmail.  # noqa: E501
        :rtype: str
        """
        return self._html_content

    @html_content.setter
    def html_content(self, html_content):
        """Sets the html_content of this SendSmtpEmail.

        HTML body of the message ( Mandatory if 'templateId' is not passed, ignored if 'templateId' is passed )  # noqa: E501

        :param html_content: The html_content of this SendSmtpEmail.  # noqa: E501
        :type: str
        """

        self._html_content = html_content

    @property
    def text_content(self):
        """Gets the text_content of this SendSmtpEmail.  # noqa: E501

        Plain Text body of the message ( Ignored if 'templateId' is passed )  # noqa: E501

        :return: The text_content of this SendSmtpEmail.  # noqa: E501
        :rtype: str
        """
        return self._text_content

    @text_content.setter
    def text_content(self, text_content):
        """Sets the text_content of this SendSmtpEmail.

        Plain Text body of the message ( Ignored if 'templateId' is passed )  # noqa: E501

        :param text_content: The text_content of this SendSmtpEmail.  # noqa: E501
        :type: str
        """

        self._text_content = text_content

    @property
    def subject(self):
        """Gets the subject of this SendSmtpEmail.  # noqa: E501

        Subject of the message. Mandatory if 'templateId' is not passed  # noqa: E501

        :return: The subject of this SendSmtpEmail.  # noqa: E501
        :rtype: str
        """
        return self._subject

    @subject.setter
    def subject(self, subject):
        """Sets the subject of this SendSmtpEmail.

        Subject of the message. Mandatory if 'templateId' is not passed  # noqa: E501

        :param subject: The subject of this SendSmtpEmail.  # noqa: E501
        :type: str
        """

        self._subject = subject

    @property
    def reply_to(self):
        """Gets the reply_to of this SendSmtpEmail.  # noqa: E501


        :return: The reply_to of this SendSmtpEmail.  # noqa: E501
        :rtype: SendSmtpEmailReplyTo
        """
        return self._reply_to

    @reply_to.setter
    def reply_to(self, reply_to):
        """Sets the reply_to of this SendSmtpEmail.


        :param reply_to: The reply_to of this SendSmtpEmail.  # noqa: E501
        :type: SendSmtpEmailReplyTo
        """

        self._reply_to = reply_to

    @property
    def attachment(self):
        """Gets the attachment of this SendSmtpEmail.  # noqa: E501

        Pass the absolute URL (no local file) or the base64 content of the attachment. Name can be used in both cases to define the attachment name. It is mandatory in case of content. Extension allowed: xlsx, xls, ods, docx, docm, doc, csv, pdf, txt, gif, jpg, jpeg, png, tif, tiff, rtf, bmp, cgm, css, shtml, html, htm, zip, xml, ppt, pptx, tar, ez, ics, mobi, msg, pub and eps ( Ignored if 'templateId' is passed )  # noqa: E501

        :return: The attachment of this SendSmtpEmail.  # noqa: E501
        :rtype: list[SendSmtpEmailAttachment]
        """
        return self._attachment

    @attachment.setter
    def attachment(self, attachment):
        """Sets the attachment of this SendSmtpEmail.

        Pass the absolute URL (no local file) or the base64 content of the attachment. Name can be used in both cases to define the attachment name. It is mandatory in case of content. Extension allowed: xlsx, xls, ods, docx, docm, doc, csv, pdf, txt, gif, jpg, jpeg, png, tif, tiff, rtf, bmp, cgm, css, shtml, html, htm, zip, xml, ppt, pptx, tar, ez, ics, mobi, msg, pub and eps ( Ignored if 'templateId' is passed )  # noqa: E501

        :param attachment: The attachment of this SendSmtpEmail.  # noqa: E501
        :type: list[SendSmtpEmailAttachment]
        """

        self._attachment = attachment

    @property
    def headers(self):
        """Gets the headers of this SendSmtpEmail.  # noqa: E501


        :return: The headers of this SendSmtpEmail.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._headers

    @headers.setter
    def headers(self, headers):
        """Sets the headers of this SendSmtpEmail.


        :param headers: The headers of this SendSmtpEmail.  # noqa: E501
        :type: dict(str, str)
        """

        self._headers = headers

    @property
    def template_id(self):
        """Gets the template_id of this SendSmtpEmail.  # noqa: E501

        Id of the template  # noqa: E501

        :return: The template_id of this SendSmtpEmail.  # noqa: E501
        :rtype: int
        """
        return self._template_id

    @template_id.setter
    def template_id(self, template_id):
        """Sets the template_id of this SendSmtpEmail.

        Id of the template  # noqa: E501

        :param template_id: The template_id of this SendSmtpEmail.  # noqa: E501
        :type: int
        """

        self._template_id = template_id

    @property
    def params(self):
        """Gets the params of this SendSmtpEmail.  # noqa: E501


        :return: The params of this SendSmtpEmail.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this SendSmtpEmail.


        :param params: The params of this SendSmtpEmail.  # noqa: E501
        :type: dict(str, str)
        """

        self._params = params

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
        if not isinstance(other, SendSmtpEmail):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
