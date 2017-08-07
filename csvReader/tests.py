import unittest
from csvReader import csvReader as csv
#TODO: test csvReader2
from csvReader import csvReader2 as csv2


class CsvReaderTestCase(unittest.TestCase):
    def test_Labels(self):
        default_lables = csv.Labels()
        self.assertEquals(default_lables.heading_row, None)
        self.assertEquals(default_lables.unit_row, None)
        self.assertEquals(default_lables.data_row, 0)
        self.assertEquals(default_lables.headings, ["yyyy", "mm", "tmax", "tmin", "af", "rain", "sun"])
        self.assertEquals(default_lables.columns, 7)
        self.assertEquals(default_lables.units, ["degC", "degC", "days", "mm", "hours"])
        self.assertEquals(default_lables.labels, 5)

        modified_lables = csv.Labels(0,1,2,"x, y, z","rads, km")
        self.assertEquals(modified_lables.heading_row, 0)
        self.assertEquals(modified_lables.unit_row, 1)
        self.assertEquals(modified_lables.data_row, 2)
        self.assertEquals(modified_lables.headings, ["x","y","z"])
        self.assertEquals(modified_lables.columns, 3)
        self.assertEquals(modified_lables.units, ["rads","km"])
        self.assertEquals(modified_lables.labels, 2)

    def test_Types(self):
        default_type = csv.Type()
        self.assertEquals(default_type.check("this is some text 509 )*&^%$."), True)
        self.assertEquals(type(default_type.convert("2000")), str)

        custom_type= csv.Type(r"^[0-9]*[1-9][0-9]*$", int)
        self.assertEquals(custom_type.check("120"), True)
        self.assertEquals(custom_type.check("90.0"), False)
        self.assertEquals(type(custom_type.convert("120")), int)
        self.assertEquals(custom_type.convert("120"), 120)
        self.assertRaises(ValueError, lambda: custom_type.convert("NAN"))
        self.assertRaises(ValueError, lambda: custom_type.convert("random_string"))

    def test_DataTypes(self):
        """
        could do with a lot more tests to make sure each of the default types has full coverage
        """
        data_types = csv.DataTypes([0,1,2,3,4],[csv.Type(r"^1$")]).types
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

class CsvReader2TestCase(unittest.TestCase):
    def setUp(self):
        self.meta = csv2.MetaData()
        self.meta.types["custom"] = csv.Type(r"^1$", int)
        
    def test_Types(self):
        default_type = csv2.Type()
        self.assertEquals(default_type.check("this is some text 509 )*&^%$."), True)
        self.assertEquals(type(default_type.convert("2000")), str)

        custom_type= csv2.Type(r"^[0-9]*[1-9][0-9]*$", int)
        self.assertEquals(custom_type.check("120"), True)
        self.assertEquals(custom_type.check("90.0"), False)
        self.assertEquals(type(custom_type.convert("120")), int)
        self.assertEquals(custom_type.convert("120"), 120)
        self.assertRaises(ValueError, lambda: custom_type.convert("NAN"))
        self.assertRaises(ValueError, lambda: custom_type.convert("random_string"))

    def test_Fields(self):
        self.assertEquals(self.do_Field_check("","universal"),True)
        self.assertEquals(self.do_Field_check("","date"),False)
        self.assertEquals(self.do_Field_check("","integer"),False)
        self.assertEquals(self.do_Field_check("","float"),False)
        self.assertEquals(self.do_Field_check("f5;-","universal"),True)
        self.assertEquals(self.do_Field_check("f5;-","date"),False)
        self.assertEquals(self.do_Field_check("f5;-","integer"),False)
        self.assertEquals(self.do_Field_check("f5;-","float"),False)
        self.assertEquals(self.do_Field_check("f5;-","custom"),False)
        self.assertEquals(self.do_Field_check("0010","date"),True)
        self.assertEquals(self.do_Field_check("0010","integer"),True)
        self.assertEquals(self.do_Field_check("0010","float"),True)
        self.assertEquals(self.do_Field_check("0010","custom"),False)
        self.assertEquals(self.do_Field_check("00100","date"),False)
        self.assertEquals(self.do_Field_check("00100","integer"),True)
        self.assertEquals(self.do_Field_check("00100","float"),True)
        self.assertEquals(self.do_Field_check("00100","custom"),False)
        self.assertEquals(self.do_Field_check("-100","integer"),True)
        self.assertEquals(self.do_Field_check("-100","float"),True)
        self.assertEquals(self.do_Field_check("-10.0","integer"),False)
        self.assertEquals(self.do_Field_check("1","custom"),True)
        self.assertEquals(self.do_Field_convert("10","integer"),10)
        self.assertEquals(type(self.do_Field_convert("10","integer")), int)
        self.assertRaises(ValueError, lambda:self.do_Field_convert("-10.0","integer"))

    def do_Field_check(self, to_check,type):
        field =csv2.Field("name",type)
        field.activate_type(self.meta.types)
        return field.type.check(to_check)

    def do_Field_convert(self, to_convert,type):
        field =csv2.Field("name",type)
        field.activate_type(self.meta.types)
        return field.type.convert(to_convert)
        
if __name__ == '__main__':
    unittest.main()
