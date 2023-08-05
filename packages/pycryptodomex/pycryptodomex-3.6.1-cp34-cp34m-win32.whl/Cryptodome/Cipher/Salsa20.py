# -*- coding: utf-8 -*-
#
# Cipher/Salsa20.py : Salsa20 stream cipher (http://cr.yp.to/snuffle.html)
#
# Contributed by Fabrizio Tarizzo <fabrizio@fabriziotarizzo.org>.
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

from Cryptodome.Util.py3compat import _copy_bytes
from Cryptodome.Util._raw_api import (load_pycryptodome_raw_lib,
                                  create_string_buffer,
                                  get_raw_buffer, VoidPointer,
                                  SmartPointer, c_size_t,
                                  c_uint8_ptr)

from Cryptodome.Random import get_random_bytes

_raw_salsa20_lib = load_pycryptodome_raw_lib("Cryptodome.Cipher._Salsa20",
                    """
                    int Salsa20_stream_init(uint8_t *key, size_t keylen,
                                            uint8_t *nonce, size_t nonce_len,
                                            void **pSalsaState);
                    int Salsa20_stream_destroy(void *salsaState);
                    int Salsa20_stream_encrypt(void *salsaState,
                                               const uint8_t in[],
                                               uint8_t out[], size_t len);
                    """)


class Salsa20Cipher:
    """Salsa20 cipher object. Do not create it directly. Use :py:func:`new`
    instead.

    :var nonce: The nonce with length 8
    :vartype nonce: byte string
    """

    def __init__(self, key, nonce):
        """Initialize a Salsa20 cipher object

        See also `new()` at the module level."""

        if len(key) not in key_size:
            raise ValueError("Incorrect key length for Salsa20 (%d bytes)" % len(key))

        if len(nonce) != 8:
            raise ValueError("Incorrect nonce length for Salsa20 (%d bytes)" %
                             len(nonce))

        self.nonce = _copy_bytes(None, None, nonce)

        self._state = VoidPointer()
        result = _raw_salsa20_lib.Salsa20_stream_init(
                        c_uint8_ptr(key),
                        c_size_t(len(key)),
                        c_uint8_ptr(nonce),
                        c_size_t(len(nonce)),
                        self._state.address_of())
        if result:
            raise ValueError("Error %d instantiating a Salsa20 cipher")
        self._state = SmartPointer(self._state.get(),
                                   _raw_salsa20_lib.Salsa20_stream_destroy)

        self.block_size = 1
        self.key_size = len(key)

    def encrypt(self, plaintext):
        """Encrypt a piece of data.

        :param plaintext: The data to encrypt, of any size.
        :type plaintext: bytes/bytearray/memoryview
        :returns: the encrypted byte string, of equal length as the
          plaintext.
        """

        ciphertext = create_string_buffer(len(plaintext))
        result = _raw_salsa20_lib.Salsa20_stream_encrypt(
                                         self._state.get(),
                                         c_uint8_ptr(plaintext),
                                         ciphertext,
                                         c_size_t(len(plaintext)))
        if result:
            raise ValueError("Error %d while encrypting with Salsa20" % result)
        return get_raw_buffer(ciphertext)

    def decrypt(self, ciphertext):
        """Decrypt a piece of data.

        :param ciphertext: The data to decrypt, of any size.
        :type ciphertext: bytes/bytearray/memoryview
        :returns: the decrypted byte string, of equal length as the
          ciphertext.
        """

        try:
            return self.encrypt(ciphertext)
        except ValueError as e:
            raise ValueError(str(e).replace("enc", "dec"))

def new(key, nonce=None):
    """Create a new Salsa20 cipher

    :keyword key: The secret key to use. It must be 16 or 32 bytes long.
    :type key: bytes/bytearray/memoryview

    :keyword nonce:
        A value that must never be reused for any other encryption
        done with this key. It must be 8 bytes long.

        If not provided, a random byte string will be generated (you can read
        it back via the ``nonce`` attribute of the returned object).
    :type nonce: bytes/bytearray/memoryview

    :Return: a :class:`Cryptodome.Cipher.Salsa20.Salsa20Cipher` object
    """

    if nonce is None:
        nonce = get_random_bytes(8)

    return Salsa20Cipher(key, nonce)

# Size of a data block (in bytes)
block_size = 1

# Size of a key (in bytes)
key_size = (16, 32)

