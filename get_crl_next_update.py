#!/usr/bin/env python


import types
from Crypto.Util import asn1
import datetime as dt
from pytz import UTC
from urllib2 import urlopen
import sys


time_formats = {
    23: lambda(obj): decode_time(obj, "%y%m%d%H%M%SZ"),
    24: lambda(obj): decode_time(obj, "%Y%m%d%H%M%SZ"),
    }


def decode_time(obj, format):
    return dt.datetime.strptime(obj.payload, format).replace(tzinfo=UTC)


def crl_dates(crl_der):
    crl_seq = asn1.DerSequence()
    crl_seq.decode(crl_der)
    if len(crl_seq) != 3: raise ValueError("unknown crl format")
    tbsCertList = asn1.DerSequence()
    tbsCertList.decode(crl_seq[0])
    thisUpdate = asn1.DerObject()
    nextUpdate = asn1.DerObject()
    if isinstance(tbsCertList[0], types.StringTypes): # CRL v1
        thisUpdate.decode(tbsCertList[2])
        nextUpdate.decode(tbsCertList[3])
    else:
        if tbsCertList[0] > 1: raise ValueError("unsupported CRL profile version: %d" % tbsCertList[0])
        thisUpdate.decode(tbsCertList[3])
        nextUpdate.decode(tbsCertList[4])
    if thisUpdate.typeTag not in time_formats or \
       nextUpdate.typeTag not in time_formats:
        raise ValueError("invalid CRL date/time fields")
    return time_formats[nextUpdate.typeTag](nextUpdate)


if __name__ == "__main__":
    nextUpdate = crl_dates(urlopen(sys.argv[1].replace(" ", "%20")).read())
    currentDate = dt.datetime.now()
    print nextUpdate
    print currentDate.replace(tzinfo=UTC)

