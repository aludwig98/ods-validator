from enum import Enum

class FILE_STATUS(Enum):
    FILE_STATUS_UNKNOWN = 0
    FILE_STATUS_OK = 1
    FILE_STATUS_ERROR = 3

class ODS_Data_Types(Enum):
    def __repr__(self):
        return self.name

    DATE_TYPE    = 0

    # Integers
    NUM6_TYPE    = 1
    NUM8_TYPE    = 2 
    NUMBER_TYPE  = 3
    NUMBER_10_TYPE = 4
    
    # Floats
    NUM6V2_TYPE  = 5
    NUM11V2_TYPE = 6
    NUM13V4_TYPE = 7
    
    # Characters   
    CHAR3_TYPE   = 8
    CHAR4_TYPE   = 9
    CHAR8_TYPE   = 10
    CHAR9_TYPE   = 11
    CHAR10_TYPE  = 12
    CHAR14_TYPE  = 13
    CHAR18_TYPE  = 14
    CHAR27_TYPE  = 15
    CHAR35_TYPE  = 16
    CHAR120_TYPE = 17


class ODS_Reequired_Columns_Keys(Enum):
    COLUMN_NAME = "column_name"
    REQUIRED = "required"
    DATA_TYPE = "data_type"
    WARN_IF_BLANK = "warn_if_blank"
    SPECIAL_VALIDATOR = "special_validator"

ODS_Integer_Data_Types = {
    ODS_Data_Types.NUM6_TYPE: 6,
    ODS_Data_Types.NUM8_TYPE: 8,
    ODS_Data_Types.NUMBER_TYPE: 9,
}

ODS_Float_Data_Types = {
    ODS_Data_Types.NUM6V2_TYPE: {"total": 9, "before": 6, "after": 2},
    ODS_Data_Types.NUM11V2_TYPE: {"total": 14, "before": 11, "after": 2},
    ODS_Data_Types.NUM13V4_TYPE: {"total": 18, "before": 13, "after": 4},
}

ODS_Char_Data_Types = {
    ODS_Data_Types.CHAR3_TYPE: 3,
    ODS_Data_Types.CHAR4_TYPE: 4,
    ODS_Data_Types.CHAR8_TYPE: 8,
    ODS_Data_Types.CHAR9_TYPE: 9,
    ODS_Data_Types.CHAR10_TYPE: 10,
    ODS_Data_Types.CHAR14_TYPE: 14,
    ODS_Data_Types.CHAR18_TYPE: 18,
    ODS_Data_Types.CHAR27_TYPE: 27,
    ODS_Data_Types.CHAR35_TYPE: 35,
    ODS_Data_Types.CHAR120_TYPE: 120,
}

ODS_Column_Label_Lookup = [
    "A", #0
    "B", #1
    "C", #2
    "D", #3
    "E", #4
    "F", #5
    "G", #6
    "H", #7
    "I", #8
    "J", #9
    "K", #10
    "L", #11
    "M", #12
    "N", #13
    "O", #14
    "P", #15
    "Q", #16
    "R", #17
    "S", #18
    "T", #19
    "U", #20
    "V", #21
    "W", #22
    "X", #23
    "Y", #24
    "Z", #25
]

class BeforeDecimalTooLong(Exception):
    pass

class AfterDecimalTooLong(Exception):
    pass

class DataTooLong(Exception):
    pass

class DataEmptyWarning(Exception):
    pass

class DataEmptyError(Exception):
    pass

class PossibleIssue(Exception):
    pass

class WrongDateFormat(Exception):
    pass
