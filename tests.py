import unittest
from csvReader.csvReader import *


class LabelsTestCase(unittest.TestCase):
    def test_Labels_default(self):
        default_lables = Labels()
        self.assertEquals(default_lables.heading_row, None)
        self.assertEquals(default_lables.unit_row, None)
        self.assertEquals(default_lables.data_row, 0)
        self.assertEquals(default_lables.headings, ["yyyy", "mm", "tmax", "tmin", "af", "rain", "sun"])
        self.assertEquals(default_lables.columns, 7)
        self.assertEquals(default_lables.units, ["degC", "degC", "days", "mm", "hours"])
        self.assertEquals(default_lables.labels, 5)

    def test_Labels_modified(self):
        modified_lables = Labels(0,1,2,"x, y, z","rads, km")
        self.assertEquals(modified_lables.heading_row, 0)
        self.assertEquals(modified_lables.unit_row, 1)
        self.assertEquals(modified_lables.data_row, 2)
        self.assertEquals(modified_lables.headings, ["x","y","z"])
        self.assertEquals(modified_lables.columns, 3)
        self.assertEquals(modified_lables.units, ["rads","km"])
        self.assertEquals(modified_lables.labels, 2)

class
if __name__ == '__main__':
    unittest.main()
