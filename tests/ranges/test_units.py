import unittest

from ranges.units import DistanceUnit, WeightUnit

class TestDistanceUnit(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(DistanceUnit.from_string("cm"), DistanceUnit.CENTIMETERS)
        self.assertEqual(DistanceUnit.from_string("in"), DistanceUnit.INCHES)
        self.assertEqual(DistanceUnit.from_string("in."), DistanceUnit.INCHES)
        self.assertEqual(DistanceUnit.from_string("inches"), DistanceUnit.INCHES)
        self.assertEqual(DistanceUnit.from_string("mm"), DistanceUnit.MILLIMETERS)
        self.assertIsNone(DistanceUnit.from_string(None))

        with self.assertRaises(ValueError):
            DistanceUnit.from_string("g")
        
        with self.assertRaises(ValueError):
            DistanceUnit.from_string("oz")
        
        with self.assertRaises(ValueError):
            DistanceUnit.from_string("mmg")
        
        with self.assertRaises(ValueError):
            DistanceUnit.from_string("")
        
        with self.assertRaises(ValueError):
            DistanceUnit.from_string(123)
    
    def test_split_value(self):
        value, unit = DistanceUnit.split_value("143mm")
        self.assertEqual(value, "143")
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        
        value, unit = DistanceUnit.split_value("142 mm")
        self.assertEqual(value, "142")
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)
        
        value, unit = DistanceUnit.split_value(" 123 mm")
        self.assertEqual(value, "123")
        self.assertEqual(unit, DistanceUnit.MILLIMETERS)

        value, unit = DistanceUnit.split_value("65+")
        self.assertEqual(value, "65+")
        self.assertIsNone(unit)

        value, unit = DistanceUnit.split_value(" 123 min")
        self.assertEqual(value, "123 min")
        self.assertIsNone(unit)

        value, unit = DistanceUnit.split_value("12f in")
        self.assertEqual(value, "12f")
        self.assertEqual(unit, DistanceUnit.INCHES)

        value, unit = DistanceUnit.split_value("12 m")
        self.assertEqual(value, "12 m")
        self.assertIsNone(unit)

        with self.assertRaises(ValueError):
            value, unit = DistanceUnit.split_value(None)




class TestWeightUnit(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(WeightUnit.from_string("g"), WeightUnit.GRAMS)
        self.assertEqual(WeightUnit.from_string("oz"), WeightUnit.OUNCES)
        self.assertIsNone(WeightUnit.from_string(None))

        with self.assertRaises(ValueError):
            WeightUnit.from_string("not recorded")
        
        with self.assertRaises(ValueError):
            WeightUnit.from_string("inchesg")
        
        with self.assertRaises(ValueError):
            WeightUnit.from_string("mm")
        
        with self.assertRaises(ValueError):
            WeightUnit.from_string("")
        
        with self.assertRaises(ValueError):
            WeightUnit.from_string(14)
    
    def test_split_value(self):
        value, unit = WeightUnit.split_value("143g")
        self.assertEqual(value, "143")
        self.assertEqual(unit, WeightUnit.GRAMS)
        
        value, unit = WeightUnit.split_value("142 g")
        self.assertEqual(value, "142")
        self.assertEqual(unit, WeightUnit.GRAMS)
        
        value, unit = WeightUnit.split_value(" 123 g")
        self.assertEqual(value, "123")
        self.assertEqual(unit, WeightUnit.GRAMS)

        value, unit = WeightUnit.split_value("65+")
        self.assertEqual(value, "65+")
        self.assertIsNone(unit)

        value, unit = WeightUnit.split_value(" 123 min")
        self.assertEqual(value, "123 min")
        self.assertIsNone(unit)

        value, unit = WeightUnit.split_value("12f oz")
        self.assertEqual(value, "12f")
        self.assertEqual(unit, WeightUnit.OUNCES)

        value, unit = WeightUnit.split_value("12 mm")
        self.assertEqual(value, "12 mm")
        self.assertIsNone(unit)

        with self.assertRaises(ValueError):
            value, unit = WeightUnit.split_value(None)

if __name__ == "__main__":
    unittest.main()