# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2013 YAMAMOTO Takashi <yamamoto at valinux co jp>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Copyright 2015 FUJITSU LIMITED. 
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#   http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 
# 


# there are two representations of value and mask this module deal with.
#
# "user"
#   (value, mask) or value.  the latter means no mask.
#   value and mask are strings.
#
# "internal"
#   value and mask are on-wire bytes.
#   mask is None if no mask.

import itertools
import struct
import ofproto_common
from ofproto_parser import msg_pack_into

from ryu.lib import addrconv
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
import math
# -------------------------- Fujitsu code end -------------------------------

class TypeDescr(object):
    pass


class IntDescr(TypeDescr):
    def __init__(self, size):
        self.size = size

    def to_user(self, bin):
        i = 0
        for x in xrange(self.size):
            c = bin[:1]
            i = i * 256 + ord(c)
            bin = bin[1:]
        return i

    def from_user(self, i):
        bin = ''
        for x in xrange(self.size):
            bin = chr(i & 255) + bin
            i /= 256
        return bin

# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
    def to_user_exp(self, bin ,size):
        i = 0
        for x in xrange(size):
            c = bin[:1]
            i = i * 256 + ord(c)
            bin = bin[1:]
        return i
# -------------------------- Fujitsu code end -------------------------------

Int1 = IntDescr(1)
Int2 = IntDescr(2)
Int3 = IntDescr(3)
Int4 = IntDescr(4)
Int8 = IntDescr(8)
Int32 = IntDescr(32)
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
Int5 = IntDescr(5)
Int14 = IntDescr(14)
# -------------------------- Fujitsu code end -------------------------------

class MacAddr(TypeDescr):
    size = 6
    to_user = addrconv.mac.bin_to_text
    from_user = addrconv.mac.text_to_bin


class IPv4Addr(TypeDescr):
    size = 4
    to_user = addrconv.ipv4.bin_to_text
    from_user = addrconv.ipv4.text_to_bin


class IPv6Addr(TypeDescr):
    size = 16
    to_user = addrconv.ipv6.bin_to_text
    from_user = addrconv.ipv6.text_to_bin


class UnknownType(TypeDescr):
    import base64

    to_user = staticmethod(base64.b64encode)
    from_user = staticmethod(base64.b64decode)


OFPXMC_OPENFLOW_BASIC = 0x8000
OFPXMC_EXPERIMENTER = 0xffff


class _OxmClass(object):
    def __init__(self, name, num, type_):
        self.name = name
        self.oxm_type = num | (self._class << 7)
        self.type = type_


class OpenFlowBasic(_OxmClass):
    _class = OFPXMC_OPENFLOW_BASIC

    def __init__(self, name, num, type_):
        super(OpenFlowBasic, self).__init__(name, num, type_)
        self.num = self.oxm_type

class OpenFlowExprtimenter(object):
    _class = OFPXMC_EXPERIMENTER

    def __init__(self, name, num, type_):
        self.name = name
        self.num = num | (self._class << 7)
        self.type = type_

class _Experimenter(_OxmClass):
    _class = OFPXMC_EXPERIMENTER


class ONFExperimenter(_Experimenter):
    experimenter_id = ofproto_common.ONF_EXPERIMENTER_ID

    def __init__(self, name, num, type_):
        super(ONFExperimenter, self).__init__(name, 0, type_)
        self.num = (ONFExperimenter, num)
        self.exp_type = num


def generate(modname):
    import sys
    import string
    import functools

    mod = sys.modules[modname]

    def add_attr(k, v):
        setattr(mod, k, v)

    for i in mod.oxm_types:
        uk = string.upper(i.name)
        if isinstance(i.num, tuple):
            continue
        oxm_class = i.num >> 7
        if oxm_class == OFPXMC_OPENFLOW_BASIC:
            ofpxmt = i.num & 0x3f
            td = i.type
            add_attr('OFPXMT_OFB_' + uk, ofpxmt)
            add_attr('OXM_OF_' + uk, mod.oxm_tlv_header(ofpxmt, td.size))
            add_attr('OXM_OF_' + uk + '_W', mod.oxm_tlv_header_w(ofpxmt, td.size))
        elif oxm_class == OFPXMC_EXPERIMENTER:
            ofpxmt = i.num & 0x3f
            td = i.type
            add_attr('OFPXMT_OFB_' + uk, ofpxmt)
            add_attr('OXM_OF_' + uk, mod.oxm_tlv_header_ex(ofpxmt, td.size))
            add_attr('OXM_OF_' + uk + '_W', mod.oxm_tlv_header_ex_w(ofpxmt, td.size))
        else:
            continue

    name_to_field = dict((f.name, f) for f in mod.oxm_types)
    num_to_field = dict((f.num, f) for f in mod.oxm_types)
    add_attr('oxm_from_user', functools.partial(from_user, name_to_field))
    add_attr('oxm_to_user', functools.partial(to_user, num_to_field))
    add_attr('_oxm_field_desc', functools.partial(_field_desc, num_to_field))
    add_attr('oxm_normalize_user', functools.partial(normalize_user, mod))
    add_attr('oxm_parse', functools.partial(parse, mod))
    add_attr('oxm_serialize', functools.partial(serialize, mod))
    add_attr('oxm_to_jsondict', to_jsondict)
    add_attr('oxm_from_jsondict', from_jsondict)


def from_user(name_to_field, name, user_value):
    try:
        f = name_to_field[name]
        t = f.type
        num = f.num
    except KeyError:
        t = UnknownType
        if name.startswith('field_'):
            num = int(name.split('_')[1])
        else:
            raise KeyError('unknown match field ' + name)
    # the 'list' case below is a bit hack; json.dumps silently maps
    # python tuples into json lists.
    if isinstance(user_value, (tuple, list)):
        (value, mask) = user_value
    else:
        value = user_value
        mask = None
    if value is not None:
        value = t.from_user(value)
    if mask is not None:
        mask = t.from_user(mask)
    return num, value, mask


def to_user(num_to_field, n, v, m):
    try:
        f = num_to_field[n]
        t = f.type
        name = f.name
    except KeyError:
        t = UnknownType
        name = 'field_%d' % n
    if v is not None:
        if hasattr(t, 'size') and t.size != len(v):
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
#            raise Exception(
#                'Unexpected OXM payload length %d for %s (expected %d)'
#                % (len(v), name, t.size))
#        value = t.to_user(v)
            if name == "odu_sigid":
                value = t.to_user_exp(v, len(v))
            else:
                raise Exception(
                    'Unexpected OXM payload length %d for %s (expected %d)'
                    % (len(v), name, t.size))
        else:
            value = t.to_user(v)
# -------------------------- Fujitsu code end -------------------------------

    else:
        value = None
    if m is None:
        user_value = value
    else:
        user_value = (value, t.to_user(m))
    return name, user_value


def _field_desc(num_to_field, n):
    return num_to_field[n]


def normalize_user(mod, k, uv):
    (n, v, m) = mod.oxm_from_user(k, uv)
    # apply mask
    if m is not None:
        v = ''.join(chr(ord(x) & ord(y)) for (x, y) in itertools.izip(v, m))
    (k2, uv2) = mod.oxm_to_user(n, v, m)
    assert k2 == k
    return (k2, uv2)


# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
OFP_EXPERIMENTER_FIELD_CHG = 38
# -------------------------- Fujitsu code end -------------------------------

def parse(mod, buf, offset):
    hdr_pack_str = '!I'
    (header, ) = struct.unpack_from(hdr_pack_str, buf, offset)
    hdr_len = struct.calcsize(hdr_pack_str)
    oxm_type = header >> 9  # class|field
    oxm_hasmask = mod.oxm_tlv_header_extract_hasmask(header)
    len = mod.oxm_tlv_header_extract_length(header)
    oxm_class = oxm_type >> 7
    if oxm_class == OFPXMC_EXPERIMENTER:
        exp_hdr_pack_str = '!I'  # experimenter_id
        (exp_id, ) = struct.unpack_from(exp_hdr_pack_str, buf,
                                        offset + hdr_len)
        exp_hdr_len = struct.calcsize(exp_hdr_pack_str)
        if exp_id == ofproto_common.ONF_EXPERIMENTER_ID:
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
            '''
            onf_exp_type_pack_str = '!H'
            (exp_type, ) = struct.unpack_from(onf_exp_type_pack_str, buf,
                                              offset + hdr_len + exp_hdr_len)
            exp_hdr_len += struct.calcsize(onf_exp_type_pack_str)
            num = (ONFExperimenter, exp_type)
            '''
            num = oxm_type + OFP_EXPERIMENTER_FIELD_CHG
# -------------------------- Fujitsu code end -------------------------------
    else:
        num = oxm_type
        exp_hdr_len = 0
    value_offset = offset + hdr_len + exp_hdr_len
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
#    value_len = len - exp_hdr_len
    value_len = len
# -------------------------- Fujitsu code end -------------------------------
    value_pack_str = '!%ds' % value_len
    assert struct.calcsize(value_pack_str) == value_len
    (value, ) = struct.unpack_from(value_pack_str, buf, value_offset)
    if oxm_hasmask:
        (mask, ) = struct.unpack_from(value_pack_str, buf,
                                      value_offset + value_len)
    else:
        mask = None
# -------------------------- Fujitsu code start -----------------------------
# For optical enhancing
#    field_len = hdr_len + (header & 0xff)
    field_len = hdr_len + (header & 0xff) + exp_hdr_len
# -------------------------- Fujitsu code end -------------------------------
    return num, value, mask, field_len


def serialize(mod, n, value, mask, buf, offset):
    exp_hdr = bytearray()
    if isinstance(n, tuple):
        (cls, exp_type) = n
        desc = mod._oxm_field_desc(n)
        assert issubclass(cls, _Experimenter)
        assert isinstance(desc, cls)
        assert cls is ONFExperimenter
        onf_exp_hdr_pack_str = '!IH'  # experimenter_id, exp_type
        msg_pack_into(onf_exp_hdr_pack_str, exp_hdr, 0,
                      cls.experimenter_id, exp_type)
        assert len(exp_hdr) == struct.calcsize(onf_exp_hdr_pack_str)
        n = desc.oxm_type
        assert (n >> 7) == OFPXMC_EXPERIMENTER
    exp_hdr_len = len(exp_hdr)
    value_len = len(value)
    if mask:
        assert value_len == len(mask)
        pack_str = "!I%ds%ds%ds" % (exp_hdr_len, value_len, len(mask))
        msg_pack_into(pack_str, buf, offset,
                      (n << 9) | (1 << 8) | (exp_hdr_len + value_len * 2),
                      bytes(exp_hdr), value, mask)
    else:
        pack_str = "!I%ds%ds" % (exp_hdr_len, value_len,)
        msg_pack_into(pack_str, buf, offset,
                      (n << 9) | (0 << 8) | (exp_hdr_len + value_len),
                      bytes(exp_hdr), value)
    return struct.calcsize(pack_str)


def to_jsondict(k, uv):
    if isinstance(uv, tuple):
        (value, mask) = uv
    else:
        value = uv
        mask = None
    return {"OXMTlv": {"field": k, "value": value, "mask": mask}}


def from_jsondict(j):
    tlv = j['OXMTlv']
    field = tlv['field']
    value = tlv['value']
    mask = tlv.get('mask')
    if mask is None:
        uv = value
    else:
        uv = (value, mask)
    return (field, uv)
