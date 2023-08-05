# Copyright (c) 2014-2017 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""A shim for accessing cryptographic primitives needed by asyncssh"""

from .cipher import register_cipher, lookup_cipher

from .ec import lookup_ec_curve_by_params

# Import PyCA versions of DSA, ECDSA, RSA, and PBKDF2
from .pyca.dsa import DSAPrivateKey, DSAPublicKey
from .pyca.ec import ECDSAPrivateKey, ECDSAPublicKey, ECDH
from .pyca.rsa import RSAPrivateKey, RSAPublicKey
from .pyca.kdf import pbkdf2_hmac

# Import pyca module to get ciphers defined there registered
from . import pyca

# Import chacha20-poly1305 cipher if available
from . import chacha

# Import curve25519 DH if available
try:
    from .curve25519 import Curve25519DH
except ImportError: # pragma: no cover
    pass

# Import umac cryptographic hash if available
try:
    from .umac import umac32, umac64, umac96, umac128
except (ImportError, AttributeError, OSError): # pragma: no cover
    pass

# Import X.509 certificate support if available
try:
    from .pyca.x509 import X509Name, X509NamePattern
    from .pyca.x509 import generate_x509_certificate, import_x509_certificate
except ImportError: # pragma: no cover
    pass
