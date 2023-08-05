# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class FileServersListOptions(Model):
    """Additional parameters for list operation.

    :param filter: An OData $filter clause.. Used to filter results that are
     returned in the GET respnose.
    :type filter: str
    :param select: An OData $select clause. Used to select the properties to
     be returned in the GET respnose.
    :type select: str
    :param max_results: The maximum number of items to return in the response.
     A maximum of 1000 files can be returned. Default value: 1000 .
    :type max_results: int
    """

    _attribute_map = {
        'filter': {'key': '', 'type': 'str'},
        'select': {'key': '', 'type': 'str'},
        'max_results': {'key': '', 'type': 'int'},
    }

    def __init__(self, *, filter: str=None, select: str=None, max_results: int=1000, **kwargs) -> None:
        super(FileServersListOptions, self).__init__(**kwargs)
        self.filter = filter
        self.select = select
        self.max_results = max_results
