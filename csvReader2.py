""" Functions to facilitate reading csv files """

import sys
import os
import re


class CsvReadError(Exception):
    """Error class for reporting errors related to reading CSV files"""
    def __init__(self, value, info=""):
        self.value = value
        self.info = info


class MetaData:
    """Metadata  describing the formatting of a csv file"""
    def __init__(self,
                 cell_border=",",
                 row_border="\n",
                 empty_cell="",
                 markers="",  # "*#"
                 heading_row=1,
                 unit_row=None,
                 data_row=0
                 ):
        self.cell_border = re.compile(cell_border)
        self.row_border = re.compile(row_border)
        self.empty_cell = re.compile(empty_cell)
        self.markers = markers
        self.heading_row = heading_row
        self.unit_row = unit_row
        self.data_row = data_row
        self.types = {
            "universal":Type(),
            "date":Type(r"[0-9]{4}$", int),
            "integer":Type(r"-?[0-9]+$", int),
            "float":Type(r"-?[0-9]+\.?[0-9]*$", float),
        }


class Type:
    """
    Define the type of a field - using a regex to describe the expected format of the string read from the csv,
    and the type to which it should be converted
    """

    def __init__(self, regex = None, output_type = str):
        self.regex = regex
        self.output_type = output_type

    def check(self, string):
        """
        :param string: the string to be checked
        :return: boolean - true if the string matches the given regex
        """
        if self.regex is not None:
            return bool(re.compile(self.regex).match(string))
        return True

    def convert(self, string):
        """
        checks the given string matches the type for the field and casts it to the appropriate type
        :param string: the string to be converted
        :return: the value of the string cast into the appropriate type
        """
        if self.check(string):
            try:
                return self.output_type(string)
            except ValueError:
                raise ValueError('cannot convert "'+string+'" to type '+str(self.output_type))
        raise ValueError("Date type expects exactly 4 numeric digits")


class Field:
    def __init__(self, name, type_name="universal", units=""):
        self.name = name
        self.type_name = type_name
        self.units = units
        def activate_type(types):
            """
            find the named type in a dictionary of types, and add it to self
            :param types: a dictionary of avaliable types
            """
            try: self.type = types.get(self.type_name)
            except KeyError: raise ValueError(self.type_name+" is not a valid type")


class CsvFile:
    """
    a wrapper containing the  three other file metadata classes,
    (TableDelimiters, DataTypes and Labels)
    """
    def __init__(self,
                 metadata=MetaData(),
                 fields=[
                     Field("yyyy", "date"),
                     Field("mm", "integer"),
                     Field("tmax", "float","degC"),
                     Field("tmin", "float","degC"),
                     Field("af", "integer","days"),
                     Field("rain", "float","mm"),
                     Field("sun","float","hours")
                 ],
                 filepath = None
                 ):
        self.metadata = metadata
        for field in fields:
            field.activate_type()
        self.fields = fields
        self.num_fields =self.fields.length()
        self.filepath = filepath
        self.null_count = [0]*self.num_fields
        self.error_count = [0]*self.num_fields
        self.data =None

    def choose_file_in_dir(self, directory):
        """Terminal prompt:
        - Lists the files in the given directory
        - asks the user to select one of these files
        - returns the path to the file
        """
        try:
            files = os.listdir(directory)
        except OSError:
            raise CsvReadError("NoDataDirectory")

        num_files = len(files)
        if num_files <= 0:
            raise CsvReadError("NoDataFile")

        files.sort()
        print("Please chose a file from the following list (key in the item number): ", end=" ")

        for i in range(0, num_files):
            print("{}.{};".format(i + 1, files[i]), end="  ")
        print("")

        while True:
            try:
                item = int(sys.stdin.readline())
                if not (1 <= item <= num_files):
                    print(
                        "The value you entered was not valid: please enter a number from 1 to {}".format(num_files))
                else:
                    break
            except ValueError:
                print("The value you entered was not an integer: please try entering the item number again")

        filename = files[item - 1]
        print("Thank you - you have selected the data file:", filename)
        self.filepath = os.path.join(directory, filename)

    def read_file(self):
        """
        takes a csv file 'text' and a description of the file of type FileSettings
        checks the text is compatible with the described file type
        returns a 2d list representing the data stored in the csv file,
        (a list of the rows in the csv table)
        """
        text = self._open_file(self.filepath)
        self.read_contents(text)

    def read_contents(self, text):
        text = self._remove_markers(text)
        data, rows = self._split_strip(text)
        self._check_headings(data)
        data = self._check_type(data, rows)
        data = self._trim(data)
        self.data =data

    def _open_file(self):
        """
        opens a file, reads it and closes it
        returns an object of type file
        """
        try:
            data_file = open(self.filepath, "r")
        except OSError:
            raise CsvReadError("FileUnopenable")
        text = data_file.read()
        data_file.close()
        return text

    def _remove_markers(self, text):
        """ strip out asterics and hashes from the file"""
        for char in self.metadata.markers:
            text = text.replace(char, "")
        return text

    def _split_strip(self, text):
        """
        split the data into a 2D list and strip out whitespace,
        returns a 2D list of data and an integer representing the number of rows in this data
        """
        text = text.strip()
        data = self.metadata.row_border.split(text)
        rows = len(data)
        for i in range(rows):
            data[i] = data[i].strip()
            data[i] = self.metadata.cell_border.split(data[i])
        return data, rows

    def _check_headings(self, data):
        """
        Takes a 2d list of data and description of the data of class Labels
        checks the headings and units of this data match the description given in the labels class
        """
        heading_row = self.metadata.heading_row
        unit_row=data[self.metadata.unit_row]
        if heading_row is not None:
            headings= data[heading_row]
            if not [field.name for field in self.fields] == headings[:self.fields.length]:
                 raise CsvReadError("WrongDataHeadings", headings)
        if unit_row is not None:
            units= data[heading_row]
            if not [field.units for field in self.fields] == units[:self.fields.length]:
                raise CsvReadError("WrongDataUnits", units)

    def _check_type(self, data, rows):
        """
        Takes a 2d list of data, a description of the data of type FileSettings,
        and the number of rows in the data.

        checks the data in each column matches the expected type and converts it to the appropriate variable type
        returns the converted data, a count of any empty cells in the csv file,
        and a count of any unreadable values in the csv file.
        """

        fields = self.fields
        types = self.metadata.types
        empty_cell = self.metadata.empty_cell
        data_row = self.metadata.data_row

        for i in range(data_row, rows):
            for j in range(self.num_fields):
                if not fields[j].type.check(data[i][j]):
                    if empty_cell.match(data[i][j]):
                        self.null_count[j] += 1
                    else:
                        self.error_count[j] += 1
                    data[i][j] = None
                else:
                     data[i][j] = fields[j].type.convert(data[i][j])
        return data

    def _trim(self, data):
        """
         Takes a 2d list of data and description of the data of class Labels
         if any of the rows are longer than the number of labled columns the aditional cells are deleted
         returns the trimmed data
         """
        del data[:self.metadata.data_row]
        rows = len(data)
        for i in range(rows):
            data[i] = data[i][:self.num_fields]
        return data

