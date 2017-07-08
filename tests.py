import unittest
from csvReader.csvReader import *


class LabelsTestCase(unittest.TestCase):
    def test_Labels(self):
        default_lables = Labels()
        self.assertEquals(default_lables.heading_row, None)
        self.assertEquals(default_lables.unit_row, None)
        self.assertEquals(default_lables.data_row, 0)
        self.assertEquals(default_lables.headings, ["yyyy", "mm", "tmax", "tmin", "af", "rain", "sun"])
        self.assertEquals(default_lables.columns, 7)
        self.assertEquals(default_lables.units, ["degC", "degC", "days", "mm", "hours"])
        self.assertEquals(default_lables.labels, 5)

        modified_lables = Labels(0,1,2,"x, y, z","rads, km")
        self.assertEquals(modified_lables.heading_row, 0)
        self.assertEquals(modified_lables.unit_row, 1)
        self.assertEquals(modified_lables.data_row, 2)
        self.assertEquals(modified_lables.headings, ["x","y","z"])
        self.assertEquals(modified_lables.columns, 3)
        self.assertEquals(modified_lables.units, ["rads","km"])
        self.assertEquals(modified_lables.labels, 2)

    def test_Types(self):
        default_type = Type()
        self.assertEquals(default_type.check("this is some text 509 )*&^%$."), True)
        self.assertEquals(type(default_type.convert("2000")), str)

        custom_type= Type(r"^[0-9]*[1-9][0-9]*$", int)
        self.assertEquals(custom_type.check("120"), True)
        self.assertEquals(custom_type.check("90.0"), False)
        self.assertEquals(type(custom_type.convert("120")), int)
        self.assertEquals(custom_type.convert("120"), 120)
        self.assertRaises(ValueError, lambda: custom_type.convert("NAN"))

    def test_DataTypes(self):
        """
        could do with a lot more tests to make sure each of the default types has full coverage
        """
        data_types = DataTypes([0,1,2,3,4],[Type(r"^1$")]).types
        self.assertEquals(data_types[0].check(""),True)
        self.assertEquals(data_types[1].check(""),False)
        self.assertEquals(data_types[2].check(""),False)
        self.assertEquals(data_types[3].check(""),False)
        self.assertEquals(data_types[0].check("f5;-"),True)
        self.assertEquals(data_types[1].check("f5;-"),False)
        self.assertEquals(data_types[2].check("f5;-"),False)
        self.assertEquals(data_types[3].check("f5;-"),False)
        self.assertEquals(data_types[4].check("f5;-"),False)
        self.assertEquals(data_types[1].check("0010"),True)
        self.assertEquals(data_types[2].check("0010"),True)
        self.assertEquals(data_types[3].check("0010"),True)
        self.assertEquals(data_types[4].check("0010"),False)
        self.assertEquals(data_types[1].check("00100"),False)
        self.assertEquals(data_types[2].check("00100"),True)
        self.assertEquals(data_types[3].check("00100"),True)
        self.assertEquals(data_types[4].check("00100"),False)
        self.assertEquals(data_types[2].check("-100"),True)
        self.assertEquals(data_types[3].check("-100"),True)
        self.assertEquals(data_types[2].check("-10.0"),False)
        self.assertEquals(data_types[4].check("1"),True)


if __name__ == '__main__':
    unittest.main()
