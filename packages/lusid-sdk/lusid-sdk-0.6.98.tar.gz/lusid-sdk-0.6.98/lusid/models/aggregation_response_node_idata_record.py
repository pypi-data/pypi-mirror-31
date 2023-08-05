# coding=utf-8
# --------------------------------------------------------------------------
# Copyright © 2018 FINBOURNE TECHNOLOGY LTD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class AggregationResponseNodeIDataRecord(Model):
    """AggregationResponseNodeIDataRecord.

    :param description:
    :type description: str
    :param idx:
    :type idx: int
    :param id:
    :type id: ~lusid.models.QualifiedId
    :param properties:
    :type properties: ~lusid.models.IDataRecord
    :param children:
    :type children: list[~lusid.models.AggregationResponseNodeIDataRecord]
    """

    _attribute_map = {
        'description': {'key': 'description', 'type': 'str'},
        'idx': {'key': 'idx', 'type': 'int'},
        'id': {'key': 'id', 'type': 'QualifiedId'},
        'properties': {'key': 'properties', 'type': 'IDataRecord'},
        'children': {'key': 'children', 'type': '[AggregationResponseNodeIDataRecord]'},
    }

    def __init__(self, description=None, idx=None, id=None, properties=None, children=None):
        super(AggregationResponseNodeIDataRecord, self).__init__()
        self.description = description
        self.idx = idx
        self.id = id
        self.properties = properties
        self.children = children
