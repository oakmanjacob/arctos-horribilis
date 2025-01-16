import unittest

from decimal import Decimal
from deepdiff import DeepDiff

from ranges.specimen import Specimen, ReviewNeededException
from ranges.units import DistanceUnit, WeightUnit

class TestSpecimenParser(unittest.TestCase):
    def test_create_specimen_0(self):
        raw_record = {
            "MVZ #": "12345",
            "collector": "Richard M. Warner",
            "total": "95",
            "tail": "41",
            "hf": "11",
            "ear": "6",
            "Notch": None,
            "Crown": None,
            "unit": None,
            "wt": "4",
            "units": "g",
            "repro comments": "T 3x2",
            "testes L": "3",
            "testes W": "2",
            "emb count": None,
            "embs L": None,
            "embs R": None,
            "emb CR": None,
            "unformatted measurements": "Rt. side eaten by Siphid beetle in trap",
            "scars": None
        }

        expected_attributes = [
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "total length",
                "attribute_value": "95",
                "attribute_units": "mm",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "tail length",
                "attribute_value": "41",
                "attribute_units": "mm",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "hind foot with claw",
                "attribute_value": "11",
                "attribute_units": "mm",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "ear from notch",
                "attribute_value": "6",
                "attribute_units": "mm",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "weight",
                "attribute_value": "4",
                "attribute_units": "g",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
        ]

        expected_unitless_attributes = [
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "unformatted measurements",
                "attribute_value": "Rt. side eaten by Siphid beetle in trap",
                "attribute_date": "1982-06-28",
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "reproductive data",
                "attribute_value": "T 3x2",
                "attribute_date": "1982-06-28",
                "attribute_determiner": "Richard M. Warner",
            }
        ]

        specimen = Specimen.from_raw_record(raw_record)

        self.assertEqual(specimen.guid, "MVZ:Mamm:12345")
        self.assertEqual(specimen.collectors, "Richard M. Warner")
        self.assertEqual(specimen.common_data.unformatted_measurements, "Rt. side eaten by Siphid beetle in trap")
        self.assertEqual(specimen.reproductive_data.repro_comments, "T 3x2")
        self.assertIsNone(specimen.reproductive_data.scars)

        self.assertEqual(specimen.common_data.total_length, (Decimal(95), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.common_data.tail_length, (Decimal(41), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.common_data.hind_foot_with_claw, (Decimal(11), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.common_data.ear_from_notch, (Decimal(6), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.common_data.ear_from_crown, (None, None, None))
        self.assertEqual(specimen.common_data.weight, (Decimal(4), WeightUnit.GRAMS, None))
        
        self.assertEqual(specimen.reproductive_data.testes_length, (Decimal(3), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.reproductive_data.testes_width, (Decimal(2), DistanceUnit.MILLIMETERS, None))
        self.assertEqual(specimen.reproductive_data.embryo_count, (None, None))
        self.assertEqual(specimen.reproductive_data.embryo_count_left, (None, None))
        self.assertEqual(specimen.reproductive_data.embryo_count_right, (None, None))
        self.assertEqual(specimen.reproductive_data.crown_rump_length, (None, None, None))

        specimen.collected_date = "1982-06-28"

        attributes, unitless_attributes = specimen.export_attributes()

        self.assertEqual(len(attributes), len(expected_attributes))

        for expected_attribute in expected_attributes:
            self.assertIn(expected_attribute, attributes)

        self.assertEqual(len(unitless_attributes), len(expected_unitless_attributes))

        for expected_unitless_attribute in expected_unitless_attributes:
            self.assertIn(expected_unitless_attribute, unitless_attributes)


    def test_create_specimen_1(self):
        raw_record = {
            "MVZ #": "12345",
            "collector": "Richard M. Warner",
            "total": "14 3/8 in.",
            "tail": "13+",
            "hf": "4 5/8 ",
            "ear": "Not Recorded",
            "Notch": None,
            "Crown": None,
            "unit": "in",
            "wt": "4*",
            "units": "g",
            "repro comments": "",
            "testes L": None,
            "testes W": "  ",
            "emb count": "3",
            "embs L": "2",
            "embs R": "1",
            "emb CR": "3.123",
            "unformatted measurements": "  ",
            "scars": None
        }

        expected_attributes = [
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "total length",
                "attribute_value": "14.38",
                "attribute_units": "in",
                "attribute_date": "1982-06-28",
                "attribute_remark": "14 3/8",
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "hind foot with claw",
                "attribute_value": "4.62",
                "attribute_units": "in",
                "attribute_date": "1982-06-28",
                "attribute_remark": "4 5/8",
                "attribute_determiner": "Richard M. Warner",
            },
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "crown-rump length",
                "attribute_value": "3.123",
                "attribute_units": "in",
                "attribute_date": "1982-06-28",
                "attribute_remark": None,
                "attribute_determiner": "Richard M. Warner",
            },
        ]

        expected_unitless_attributes = [
            {
                "guid": "MVZ:Mamm:12345",
                "attribute_type": "unformatted measurements",
                "attribute_value": "\"tail length\": \"13+\", \"weight\": \"4*\"",
                "attribute_date": "1982-06-28",
                "attribute_determiner": "Richard M. Warner",
            },
        ]

        specimen = Specimen.from_raw_record(raw_record)

        self.assertEqual(specimen.guid, "MVZ:Mamm:12345")
        self.assertEqual(specimen.collectors, "Richard M. Warner")
        self.assertIsNone(specimen.common_data.unformatted_measurements)
        self.assertIsNone(specimen.reproductive_data.repro_comments)
        self.assertIsNone(specimen.reproductive_data.scars)

        self.assertEqual(specimen.common_data.total_length, (Decimal("14.38"), DistanceUnit.INCHES, "14 3/8"))
        self.assertEqual(specimen.common_data.tail_length, (None, DistanceUnit.INCHES, "13+"))
        self.assertEqual(specimen.common_data.hind_foot_with_claw, (Decimal("4.62"), DistanceUnit.INCHES, "4 5/8"))
        self.assertEqual(specimen.common_data.ear_from_notch, (None, None, None))
        self.assertEqual(specimen.common_data.ear_from_crown, (None, None, None))
        self.assertEqual(specimen.common_data.weight, (None, WeightUnit.GRAMS, "4*"))
        
        self.assertEqual(specimen.reproductive_data.testes_length, (None, None, None))
        self.assertEqual(specimen.reproductive_data.testes_width, (None, None, None))
        self.assertEqual(specimen.reproductive_data.embryo_count, (3, None))
        self.assertEqual(specimen.reproductive_data.embryo_count_left, (2, None))
        self.assertEqual(specimen.reproductive_data.embryo_count_right, (1, None))
        self.assertEqual(specimen.reproductive_data.crown_rump_length, (Decimal("3.123"), DistanceUnit.INCHES, None))

        specimen.collected_date = "1982-06-28"

        attributes, unitless_attributes = specimen.export_attributes()

        self.assertEqual(len(attributes), len(expected_attributes))

        for expected_attribute in expected_attributes:
            self.assertIn(expected_attribute, attributes)

        self.assertEqual(len(unitless_attributes), len(expected_unitless_attributes))

        for expected_unitless_attribute in expected_unitless_attributes:
            self.assertIn(expected_unitless_attribute, unitless_attributes)

    def test_review_needed(self):
        raw_record = {
            "MVZ #": "12345",
            "collector": "Richard M. Warner",
            "total": "14 3/8 in.",
            "tail": "13+",
            "hf": "4 5/8 ",
            "ear": "Not Recorded",
            "Notch": None,
            "Crown": None,
            "unit": "in",
            "wt": "4*",
            "units": "g",
            "repro comments": "",
            "testes L": None,
            "testes W": "  ",
            "emb count": "3",
            "embs L": "2",
            "embs R": "1",
            "emb CR": "3.123",
            "unformatted measurements": "  ",
            "scars": None,
            "REVIEW NEEDED": "total length needs review"
        }

        with self.assertRaises(ReviewNeededException):
            specimen = Specimen.from_raw_record(raw_record)


if __name__ == "__main__":
    unittest.main()