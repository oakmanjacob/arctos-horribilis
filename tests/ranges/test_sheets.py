import unittest

from decimal import Decimal

from ranges.sheets import SheetParser
from ranges.units import DistanceUnit, WeightUnit

class TestSheetParser(unittest.TestCase):

    def test_is_recorded(self):
        self.assertFalse(SheetParser.is_recorded("not Recorded"))
        self.assertFalse(SheetParser.is_recorded("NOT RECORDED"))
        self.assertFalse(SheetParser.is_recorded("not recorded"))
        self.assertFalse(SheetParser.is_recorded(None))
        self.assertFalse(SheetParser.is_recorded("NOT Recoded"))
        self.assertFalse(SheetParser.is_recorded("no recorded"))
        self.assertFalse(SheetParser.is_recorded(""))

        self.assertTrue(SheetParser.is_recorded("64"))
        self.assertTrue(SheetParser.is_recorded("123+"))
        self.assertTrue(SheetParser.is_recorded("123+\n in!"))
        self.assertTrue(SheetParser.is_recorded("123 in"))

    def test_parse_mvz_guid(self):
        self.assertEqual(SheetParser.parse_mvz_guid("MVZ:Mamm:12345"), "MVZ:Mamm:12345")
        self.assertEqual(SheetParser.parse_mvz_guid("Mamm:12345"), "MVZ:Mamm:12345")
        self.assertEqual(SheetParser.parse_mvz_guid("12345"), "MVZ:Mamm:12345")
        self.assertEqual(SheetParser.parse_mvz_guid(":12345"), "MVZ:Mamm:12345")
        self.assertEqual(SheetParser.parse_mvz_guid("::12345"), "MVZ:Mamm:12345")

        with self.assertRaises(ValueError, msg="Couldn't parse guid from value 'MVZ:Herp:12345'"):
            self.assertEqual(SheetParser.parse_mvz_guid("MVZ:Herp:12345"), "MVZ:Mamm:12345")

        with self.assertRaises(ValueError, msg="Cannot parse guid from None value"):
            SheetParser.parse_mvz_guid(None)
        
        with self.assertRaises(ValueError, msg="Couldn't parse guid from value '55g'"):
            SheetParser.parse_mvz_guid("55g")
        
        with self.assertRaises(ValueError, msg="Couldn't parse guid from value ''"):
            SheetParser.parse_mvz_guid("")

    def test_parse_numerical_attribute(self):
        number, unit, text = SheetParser.parse_numerical_attribute("211mm", DistanceUnit.MILLIMETERS, DistanceUnit.MILLIMETERS)
        self.assertEqual(number, Decimal(211))
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        self.assertIsNone(text)

        number, unit, text = SheetParser.parse_numerical_attribute("211 mm", DistanceUnit.MILLIMETERS, DistanceUnit.MILLIMETERS)
        self.assertEqual(number, Decimal(211))
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        self.assertIsNone(text)

        number, unit, text = SheetParser.parse_numerical_attribute(" mm", DistanceUnit.INCHES, DistanceUnit.MILLIMETERS)
        self.assertIsNone(number)
        self.assertEqual(unit, DistanceUnit.INCHES)
        self.assertEqual(text, " mm")

        number, unit, text = SheetParser.parse_numerical_attribute("1 1/8 in", None, DistanceUnit.MILLIMETERS)
        self.assertEqual(number, Decimal("1.12"))
        self.assertEqual(unit, DistanceUnit.INCHES)
        self.assertEqual(text, "1 1/8")

        number, unit, text = SheetParser.parse_numerical_attribute("42 3/8", None, DistanceUnit.MILLIMETERS)
        self.assertEqual(number, Decimal("42.38"))
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        self.assertEqual(text, "42 3/8")

        number, unit, text = SheetParser.parse_numerical_attribute("5/8", None, DistanceUnit.MILLIMETERS)
        self.assertEqual(number, Decimal("0.62"))
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        self.assertEqual(text, "5/8")

        number, unit, text = SheetParser.parse_numerical_attribute("65*", None, DistanceUnit.MILLIMETERS)
        self.assertIsNone(number)
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        self.assertEqual(text, "65*")

        number, unit, text = SheetParser.parse_numerical_attribute("65 oz", None, WeightUnit.GRAMS)
        self.assertEqual(number, Decimal("65"))
        self.assertEqual(unit, WeightUnit.OUNCES)
        self.assertIsNone(text)

        number, unit, text = SheetParser.parse_numerical_attribute(None, None, DistanceUnit.MILLIMETERS)
        self.assertIsNone(number)
        self.assertIsNone(unit)
        self.assertIsNone(text)

        number, unit, text = SheetParser.parse_numerical_attribute(None, None, None)
        self.assertIsNone(number)
        self.assertIsNone(unit)
        self.assertIsNone(text)

        with self.assertRaises(ValueError):
            number, unit, text = SheetParser.parse_numerical_attribute("123", None, "millimeteres")

        with self.assertRaises(ValueError):
            number, unit, text = SheetParser.parse_numerical_attribute("123", None, None)


if __name__ == "__main__":
    unittest.main()