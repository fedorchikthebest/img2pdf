import gostcrypto
from base64 import b32encode, b32decode
import os
import string
from random import choice
import datetime


if os.path.exists("session.key"):
    with open("session.key", "rb") as f:
        SESSION_KEY = f.read()
else:
    SESSION_KEY = gostcrypto.gostrandom.new(32)
    with open("session.key", "wb") as f:
        f.write(SESSION_KEY)


with open("key.pub", "rb") as f:
    PKEY = f.read()


def b32crypt(text, key=SESSION_KEY):
    cipher_obj = gostcrypto.gostcipher.new("kuznechik",
                                           key, gostcrypto.gostcipher.MODE_CFB)
    cipher_block = cipher_obj.encrypt(bytes(text, encoding="utf-8") + bytes("\0" * (16 - len(text)), encoding="utf-8"))
    return b32encode(cipher_block)


def b32decrypt(data, key=SESSION_KEY):
    cipher_obj = gostcrypto.gostcipher.new("kuznechik",
                                           key, gostcrypto.gostcipher.MODE_CFB)
    cipher_block = cipher_obj.decrypt(b32decode(data))
    return cipher_block.decode("utf-8")


def b32verify(signature, text):
    sign = gostcrypto.gostsignature.new(gostcrypto.gostsignature.MODE_512, 
                             gostcrypto.gostsignature.CURVES_R_1323565_1_024_2019['id-tc26-gost-3410-12-512-paramSetA'])
    if sign.verify(PKEY, text.encode("utf-8"), b32decode(signature)):
        return b32encode(SESSION_KEY)
    return b32encode(os.urandom(32))
