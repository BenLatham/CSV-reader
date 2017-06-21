""" Functions to facilitate reading csv files """

import sys
import os
import re


class CsvReadError(Exception):
    """Error class for reporting errors related to reading CSV files"""
    def __init__(self, value, info=""):
        self.value = value
        self.info = info


def choose_file_in_dir(directory):
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

    item = 1
    while True:
        try:
            item = int(sys.stdin.readline())
            if not (1 <= item <= num_files):
                print("The value you entered was not valid: please enter a number from 1 to {}".format(num_files))
            else:
                break
        except ValueError:
            print("The value you entered was not an integer: please try entering the item number again")

    filename = files[item - 1]
    print("Thank you - you have selected the data file:", filename)
    return os.path.join(directory, filename)


def open_file(filename):
    """
    opens a file, reads it and closes it
    returns an object of type file
    """
    try:
        data_file = open(filename, "r")
    except OSError:
        raise CsvReadError("FileUnopenable")
    text = data_file.read()
    data_file.close()
    return text


def read_file(text, filetype):
    """
    takes a csv file 'text' and a description of the file of type FileSettings
    checks the text is compatible with the described file type
    returns a 2d list representing the data stored in the csv file,
    (a list of the rows in the csv table)
    """
    delimiters = filetype.delimiters
    labels = filetype.labels
    text = remove_markers(text)
    data, rows = split_strip(text, delimiters)
    check_headings(data, labels)
    data, null_count, error_count = check_type(data, filetype, rows)
    data = trim(data, labels)
    report(null_count, error_count, labels)
    return data


def remove_markers(text):
    """ strip out asterics and hashes from the file"""
    markers = "*#"
    for char in markers:
        text = text.replace(char, "")
    return text


def split_strip(text, delimiters):
    """
    split the data into a 2D list and strip out whitespace,
    returns a 2D list of data and an integer representing the number of rows in this data
    """
    text = text.strip()
    data = delimiters.row_border.split(text)
    rows = len(data)
    for i in range(rows):
        data[i] = data[i].strip()
        data[i] = delimiters.cell_border.split(data[i])
    return data, rows


def check_headings(data, labels):
    """
    Takes a 2d list of data and description of the data of class Labels
    checks the headings and units of this data match the description given in the labels class
    """
    if labels.heading_row and not data[labels.heading_row][:labels.columns] == labels.headings:
        raise CsvReadError("WrongDataHeadings", data[labels.heading_row])
    if labels.unit_row and not data[labels.unit_row][:labels.labels] == labels.units:
        raise CsvReadError("WrongDataUnits", data[labels.unit_row])


def check_type(data, filetype, rows):
    """
    Takes a 2d list of data, a description of the data of type FileSettings,
    and the number of rows in the data.

    checks the data in each column matches the expected type and converts it to the appropriate variable type
    returns the converted data, a count of any empty cells in the csv file,
    and a count of any unreadable values in the csv file.
    """

    datatypes = filetype.data_types
    delimiters = filetype.delimiters
    labels = filetype.labels

    null_count = [0] * labels.columns
    error_count = [0] * labels.columns

    for i in range(labels.data_row, rows):
        for j in range(labels.columns):
            if datatypes.types[j].match(data[i][j]) is None:
                if delimiters.empty_cell.match(data[i][j]):
                    null_count[j] += 1
                else:
                    error_count[j] += 1
                data[i][j] = None
            else:
                if datatypes.types[j] == datatypes.float_type:
                    data[i][j] = float(data[i][j])
                else:
                    try:
                        data[i][j] = int(data[i][j])
                    except TypeError:
                        print(data[i[j]])
    return data, null_count, error_count


def trim(data, labels):
    """
     Takes a 2d list of data and description of the data of class Labels
     if any of the rows are longer than the number of labled columns the aditional cells are deleted
     returns the trimmed data
     """
    del data[:labels.data_row]
    rows = len(data)
    for i in range(rows):
        data[i] = data[i][:labels.columns]
    return data


def split_by_values(data, sort_col, value_range):
    """
    Takes a 2d list of data, the number of the column to sort by, and a range
    (an array of length 2, where range[0] is the min and range[1] is the max)

    sort lists by variable in the sorting column (relies on this value being of integer type)
    - for each value within the given range a separate list of lists is created
    - if a value in the rage is not found in the sorting column it will result in an empty list
    """
    data_sorted = [[] for i in range(value_range[0], value_range[1])]
    error_count = 0
    for row in data:
        if value_range[0] <= row[sort_col] < value_range[1]:
            data_sorted[row[sort_col] - value_range[0]].append(row)
        elif row[sort_col]:
            error_count += 1
    if error_count:
        print("Warning:", error_count, "rows were rejected as their values did not fall in the range(",
              value_range[0], ":", value_range[1], ")")
    return data_sorted


def transpose(data, length):
    """
    takes a 3d list and the length of the 3d list.
    transposes the columns of each of the 2d lists within this list
    """
    for i in range(length):
        data[i] = list(zip(*data[i]))
    return data


def report(null_count, error_count, labels):
    """ print a report on the success of reading the csv file to the terminal"""
    print("\nFile has been read successfully; any errors or empty cells are counted below:")
    print("Unreadable values by column:", end="")
    for i in range(labels.columns):
        print(labels.headings[i], "=", error_count[i], end="; ")
    print("\nEmpty cells by column:", end="")
    for i in range(labels.columns):
        print(labels.headings[i], "=", null_count[i], end="; ")
    print("\n")


def label(data, labels):
    """
    Takes a 2d list of data where each internal list represents a column and a description of the data of class Labels
    creates a dictionary out of the data, where each heading in the list labels.headings forms a new field in the dictionary,
    the dictionarry also has the fields "length", "units" and "headings" containing metadata
    """
    labeled_data = {"length": len(data[0]), "units": labels.units, "headings": labels.headings}
    for i in range(labels.columns):
        labeled_data[labels.headings[i]] = data[i]
    return labeled_data

# Metadata Classes describing the formatting of a csv file

class TableDelimiters:
    """markers used to delimit rows and cells, and to mark empty cells"""
    def __init__(self,
                 cell_border=",",
                 row_border="\n",
                 empty_cell="---",
                 ):
        self.cell_border = re.compile(cell_border)
        self.row_border = re.compile(row_border)
        self.empty_cell = re.compile(empty_cell)


class DataTypes:
    """
    The type of data in each row, as a comma separated string. Accepts 3 types in this list:
    dt standing for date_type;it standing for integer_type; ft standing for float type.

    Each type is defined by regular expressions; by default "dt" is precisely 4 numeric digits,
    "it" is 0 or more numeric digits, and "ft" is an optional "-" sign followed by 0 or more
    numeric digits followed optionally by a decimal point and more numeric digits.
    """
    def __init__(self,
                 types="dt, it, ft, ft, it, ft, ft",
                 date_type=r"[0-9]{4}$",
                 integer_type=r"[0-9]*$",
                 float_type=r"-?[0-9]*\.?[0-9]*$",
                 ):
        self.date_type = re.compile(date_type)
        self.short_type = re.compile(integer_type)
        self.float_type = re.compile(float_type)
        types = types.split(", ")
        self.types = []
        for x in types:
            if x == "dt":
                self.types.append(self.date_type)
            elif x == "it":
                self.types.append(self.short_type)
            elif x == "ft":
                self.types.append(self.float_type)
            else:
                self.types.append([])


class Labels:
    """
    data on the headings and units of the various columns in the file, and the rows in the file
    where this data is stored; also specified is a sort_by column, the value given must match
    one of the values in the headings list.
    """
    def __init__(self,
                 heading_row=None,
                 unit_row=None,
                 data_row=0,
                 headings="yyyy, mm, tmax, tmin, af, rain, sun",
                 units="degC, degC, days, mm, hours",
                 ):
        self.heading_row = heading_row
        self.unit_row = unit_row
        self.data_row = data_row
        self.headings = headings.split(", ")
        self.columns = len(self.headings)
        self.units = units.split(", ")
        self.labels = len(units)


class FileSettings:
    """
    a wrapper containing the  three other file metadata classes,
    (TableDelimiters, DataTypes and Labels)
    """
    def __init__(self, delimiters=TableDelimiters(),
                 data_types=DataTypes(),
                 labels=Labels()):
        self.delimiters = delimiters
        self.data_types = data_types
        self.labels = labels
