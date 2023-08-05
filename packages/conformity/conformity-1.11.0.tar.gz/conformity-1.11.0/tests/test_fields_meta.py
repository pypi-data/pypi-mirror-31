from __future__ import absolute_import, unicode_literals

import unittest

from conformity.error import Error
from conformity.fields import (
    All,
    Any,
    Boolean,
    BooleanValidator,
    Constant,
    Dictionary,
    Nullable,
    ObjectInstance,
    Polymorph,
    UnicodeString,
)


class MetaFieldTests(unittest.TestCase):
    """
    Tests meta fields
    """

    def test_nullable(self):
        constant = Constant("one", "two")
        schema = Nullable(constant)
        self.assertEqual([], schema.errors(None))
        self.assertEqual([], schema.errors("one"))
        self.assertEqual([], schema.errors("two"))
        self.assertEqual(1, len(schema.errors("three")))
        self.assertEqual({"type": "nullable", "nullable": constant.introspect()}, schema.introspect())

        boolean = Boolean(description="This is a test description")
        schema = Nullable(boolean)
        self.assertEqual([], schema.errors(None))
        self.assertIsNone(schema.errors(True))
        self.assertIsNone(schema.errors(False))
        self.assertEqual(1, len(schema.errors("true")))
        self.assertEqual(1, len(schema.errors(1)))
        self.assertEqual({"type": "nullable", "nullable": boolean.introspect()}, schema.introspect())

        string = UnicodeString()
        schema = Nullable(string)
        self.assertEqual([], schema.errors(None))
        self.assertIsNone(schema.errors("hello, world"))
        self.assertEqual(1, len(schema.errors(b"hello, world")))
        self.assertEqual({"type": "nullable", "nullable": string.introspect()}, schema.introspect())

    def test_any(self):
        schema = Any(Constant("one"), Constant("two"))
        self.assertEqual(
            schema.errors("one"),
            [],
        )
        self.assertEqual(
            schema.errors("two"),
            [],
        )
        self.assertEqual(
            len(schema.errors("three")),
            2,
        )

    def test_all(self):
        schema = All(Constant("one"), UnicodeString())
        self.assertEqual(
            schema.errors("one"),
            [],
        )
        self.assertEqual(
            len(schema.errors("two")),
            1,
        )

    def test_objectinstance(self):
        class Thing(object):
            pass

        class Thingy(Thing):
            pass

        class SomethingElse(object):
            pass

        schema = ObjectInstance(Thing)

        self.assertEqual(
            schema.errors(Thing()),
            []
        )

        # subclasses are valid
        self.assertEqual(
            schema.errors(Thingy()),
            []
        )

        self.assertEqual(
            schema.errors(SomethingElse()),
            [Error("Not an instance of Thing")]
        )

    def test_polymorph(self):

        card = Dictionary({
            "payment_type": Constant("card"),
            "number": UnicodeString(),
            "cvc": UnicodeString(description="Card Verification Code"),
        })

        bankacc = Dictionary({
            "payment_type": Constant("bankacc"),
            "routing": UnicodeString(description="US RTN or foreign equivalent"),
            "account": UnicodeString(),
        })

        schema = Polymorph(
            "payment_type",
            {
                "card": card,
                "bankacc": bankacc,
            },
        )

        self.assertEqual(
            schema.errors({
                "payment_type": "card",
                "number": "1234567890123456",
                "cvc": "000",
            }),
            [],
        )

        self.assertEqual(
            schema.errors({
                "payment_type": "bankacc",
                "routing": "13456790",
                "account": "13910399",
            }),
            [],
        )

        self.assertEqual(
            schema.introspect(),
            {
                "type": "polymorph",
                "contents_map": {
                    "bankacc": {
                        "type": "dictionary",
                        "allow_extra_keys": False,
                        "contents": {
                            "account": {"type": "unicode"},
                            "payment_type": {
                                "type": "constant",
                                "values": ["bankacc"],
                            },
                            "routing": {
                                "type": "unicode",
                                "description": "US RTN or foreign equivalent",
                            },
                        },
                        "optional_keys": [],
                    },
                    "card": {
                        "type": "dictionary",
                        "allow_extra_keys": False,
                        "contents": {
                            "cvc": {
                                "type": "unicode",
                                "description": "Card Verification Code",
                            },
                            "number": {"type": "unicode"},
                            "payment_type": {
                                "type": "constant",
                                "values": ["card"],
                            },
                        },
                        "optional_keys": [],
                    },
                },
                "switch_field": "payment_type",
            },
        )

    def test_boolean_validator(self):
        schema = BooleanValidator(
            lambda x: x.isdigit(),
            "str.isdigit()",
            "Not all digits",
        )
        # Test valid unicode and byte strings
        self.assertEqual(
            schema.errors("123"),
            [],
        )
        self.assertEqual(
            schema.errors(b"123"),
            [],
        )
        # Test invalid unicode and byte strings
        self.assertEqual(
            len(schema.errors("123a")),
            1,
        )
        self.assertEqual(
            len(schema.errors(b"123a")),
            1,
        )
        # Test bad-type errors are swallowed well
        self.assertEqual(
            len(schema.errors(344532)),
            1,
        )
        # Test introspection looks OK
        self.assertEqual(
            schema.introspect(),
            {
                "type": "boolean_validator",
                "validator": "str.isdigit()",
            },
        )
