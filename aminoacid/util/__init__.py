from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from hmac import HMAC

from .commands import *

__version__ = "0.1.2"

str_to_ts = lambda _str: int(datetime.strptime(_str, "%Y-%m-%dT%H:%M:%SZ").timestamp())
"""Convert an Amino Timestamp to a UNIX timestamp

Parameters
----------
_str : str
    The string to convert

Returns
----------
int
    The UNIX timestamp of the given Amino Timestamp
"""

def get_headers(
    data: bytes = b"", device: str = "", key: bytes = b"", v: bytes = b""
) -> dict:
    """Generate request headers

    Parameters
    ----------
    data : bytes, optional
        The request payload, by default b""
    device : str, optional
        deviceId to be sent, by default ""
    key : bytes, optional
        the key to be used in the request signature, this key has to be supplied by the user, by default b""
    v : bytes, optional
        version of the request signature, this is used as the prefix for the signature, by default b""

    Returns
    -------
    dict
        Returns the Headers
    """
    head = {
        "NDCDEVICEID": device,
        "Accept-Language": "en-US",
        "User-Agent": f"AminoAcid/{__version__} (+https://github.com/okok7711/AminoAcid)",
        "Host": "service.narvii.com",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
    }
    if data:
        head["NDC-MSG-SIG"] = b64encode(v + HMAC(key, data, sha1).digest()).decode(
            "utf-8"
        )

    return head
