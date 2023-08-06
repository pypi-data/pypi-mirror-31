# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import pytest
import six
from mbstrdecoder import *


nan = float("nan")
inf = float("inf")


class Test_to_MultiByteStrDecoder_repr:

    @pytest.mark.parametrize(["value", "expected"], [
        ["吾輩は猫である", "codec=unicode, unicode=吾輩は猫である"],
    ])
    def test_normal(self, value, expected):
        decoder = MultiByteStrDecoder(value)

        assert six.text_type(decoder) == expected


class Test_to_MultiByteStrDecoder_unicode:

    @pytest.mark.parametrize(["value", "expected"], [
        [b"", ""],
        [b"abcd", "abcd"],
    ])
    def test_normal_unicode_str(self, value, expected):
        decoder = MultiByteStrDecoder(value)
        assert decoder.unicode_str == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["", "unicode"],
        ["abcdefgh", "ascii"],
        ["吾輩は猫である", "unicode"],
    ])
    def test_normal_codec(self, value, expected):
        decoder = MultiByteStrDecoder(value)
        assert decoder.codec == expected
        assert decoder.unicode_str == value

    @pytest.mark.parametrize(["value", "codec"], [
        ["いろはにほへと", "utf_7"],
        [
            "RKBTqn1G9HIZ9onY9mCklj3+8ye7WBmu0xKMqp3ORT3pMgR5m73VXAR/5YrTZTGernMYLCPYdwIMewFY+6xOZmWwCrXjfw3sO2dYLubh9EIMrc/XEvAhMFd969G2yQkyFTNf9M8Ag94QCuBk51yQLSbxgmxJTqEw6bdC4gNTI44=",
            "ascii"
        ],
        ["マルチバイト文字", "utf_8"],
        ["ＡＢＣ", "utf_8"],
        ["吾輩は猫である", "utf_16"],
    ])
    def test_normal_encoding(self, value, codec):
        decoder = MultiByteStrDecoder(value.encode(codec))

        assert decoder.codec == codec
        assert decoder.unicode_str == value

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [True, ValueError],
        [[], ValueError],
        [1, ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            MultiByteStrDecoder(value)
