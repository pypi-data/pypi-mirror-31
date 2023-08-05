# -*- coding: utf-8 -*-
"""root link layer protocol

``jspcap.protocols.link.link`` contains both ``LINKTYPE``
and ``Link``. The former is a dictionary of link layer header
type values, registered in IANA. And the latter is a base
class for link layer protocols, eg. ARP/InARP, Ethernet,
L2TP, OSPF, RARP/DRARP and etc.

"""
# TODO: Implements DSL, EAPOL, FDDI, ISDN, NDP, PPP.


# Link Layer Protocols
# Table of corresponding protocols


from jspcap.protocols.protocol import Protocol
from jspcap.protocols.internet.internet import ETHERTYPE


__all__ = ['Link', 'LINKTYPE']


# ##############################################################################
# # for unknown reason and never-encountered situation, at current time
# # we have to change the working directory to import from parent folders
#
# import os
# import sys
# sys.path.insert(1, os.path.join(sys.path[0], '..'))
#
# from protocol import Protocol
#
# del sys.path[1]
#
# # and afterwards, we recover the whole scene back to its original state
# ##############################################################################


# Link-Layer Header Type Values
LINKTYPE = {
    0 : 'Null',     # BSD loopback encapsulation
    1 : 'Ethernet', # IEEE 802.3 Ethernet
  101 : 'Raw',      # Raw IP
  228 : 'IPv4',     # Raw IPv4
  229 : 'IPv6',     # Raw IPv6
  248 : 'SCTP',     # SCTP packets
}


class Link(Protocol):
    """Abstract base class for link layer protocol family.

    Properties:
        * name -- str, name of corresponding procotol
        * info -- Info, info dict of current instance
        * alias -- str, acronym of corresponding procotol
        * layer -- str, `Link`
        * length -- int, header length of corresponding protocol
        * protocol -- str, name of next layer protocol
        * protochain -- ProtoChain, protocol chain of current instance

    Attributes:
        * _file -- BytesIO, bytes to be extracted
        * _info -- Info, info dict of current instance
        * _protos -- ProtoChain, protocol chain of current instance

    Utilities:
        * _read_protos -- read next layer protocol type
        * _read_fileng -- read file buffer
        * _read_unpack -- read bytes and unpack to integers
        * _read_binary -- read bytes and convert into binaries
        * _decode_next_layer -- decode next layer protocol type
        * _import_next_layer -- import next layer protocol extractor

    """
    __layer__ = 'Link'

    ##########################################################################
    # Properties.
    ##########################################################################

    # protocol layer
    @property
    def layer(self):
        """Protocol layer."""
        return self.__layer__

    ##########################################################################
    # Utilities.
    ##########################################################################

    def _read_protos(self, size):
        """Read next layer protocol type.

        Keyword arguments:
            size  -- int, buffer size

        """
        _byte = self._read_unpack(size)
        _prot = ETHERTYPE.get(_byte)
        return _prot

    def _import_next_layer(self, proto, length):
        """Import next layer extractor.

        Keyword arguments:
            proto -- str, next layer protocol name
            length -- int, valid (not padding) length

        Protocols:
            * ARP -- data link layer
            * RARP -- data link layer
            * CTag -- data link layer
            * IPv4 -- internet layer
            * IPv6 -- internet layer
            * IPX -- internet layer

        """
        if proto == 'ARP':
            from jspcap.protocols.link.arp import ARP as Protocol
        elif proto == 'RARP':
            from jspcap.protocols.link.rarp import RARP as Protocol
        elif proto == 'CTag':
            from jspcap.protocols.link.ctag import CTag as Protocol
        elif proto == 'IPv4':
            from jspcap.protocols.internet.ipv4 import IPv4 as Protocol
        elif proto == 'IPv6':
            from jspcap.protocols.internet.ipv6 import IPv6 as Protocol
        elif proto == 'IPX':
            from jspcap.protocols.internet.ipx import IPX as Protocol
        else:
            data = self._file.read(*[length]) or None
            return data, None, None
        next_ = Protocol(self._file, length)
        return next_.info, next_.protochain, next_.alias
