from datetime import datetime
from distutils.log import warn
from tkinter.tix import COLUMN
import traceback
import typing
from xmlrpc.client import boolean
from ODS_COMMON.ods_file import ODS_File
import ODS_COMMON.ods_constants as ODS_CONSTS
from ODS_COMMON.ods_constants import DataEmpty, ODS_Char_Data_Types, ODS_Data_Types, ODS_Data_Type_Strings, ODS_Column_Label_Lookup, AfterDecimalTooLong, BeforeDecimalTooLong, DataTooLong, ODS_Float_Data_Types, ODS_Integer_Data_Types
from ODS_COMMON.ods_constants import ODS_Reequired_Columns_Keys as RCKeys

class ODS_Validator:
    def __init__(self):
        self.required_sheets = ["Other_Grants_V3", 
                                "Other_Options_V3", 
                                "Other_Acquisition_V3", 
                                "Other_RestrictedSecurities_V3", 
                                "Other_OtherBenefits_V3",
                                "Other_Convertible_V3",
                                "Other_Notional_V3",
                                "Other_Enhancement_V3",
                                "Other_Sold_V3",
                                ]
        self.required_columns = {
            "Other_Grants_V3": {
                0: {RCKeys.COLUMN_NAME:"1.\nDate of grant\n(yyyy-mm-dd)",RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME:"2.\nNumber of employees granted options", RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.NUM6_TYPE, RCKeys.WARN_IF_BLANK: True},
                2: {RCKeys.COLUMN_NAME:"3.\nUnrestricted market value of a security at date of grant\n£\ne.g. 10.1234",RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                3: {RCKeys.COLUMN_NAME:"4.\nNumber of securities over which options granted\ne.g. 100.00",RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
            },
            "Other_Options_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\nyyyy-mm-dd',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM8_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.scheme_ref_num_validator},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance Number\n(if applicable)', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nDate of grant of option subject to the reportable event\nyyyy-mm-dd',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nGrantor company name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR120_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nGrantor company address line 1',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                11: {RCKeys.COLUMN_NAME: '12.\nGrantor company address line 2',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                12: {RCKeys.COLUMN_NAME: '13.\nGrantor company address line 3',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                13: {RCKeys.COLUMN_NAME: '14.\nGrantor company address line 4',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                14: {RCKeys.COLUMN_NAME: '15.\nGrantor company country',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                15: {RCKeys.COLUMN_NAME: '16.\nGrantor company postcode',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR8_TYPE, RCKeys.WARN_IF_BLANK: False},
                16: {RCKeys.COLUMN_NAME: '17.\nGrantor Company Registration Number (CRN) , if applicable',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: True},
                17: {RCKeys.COLUMN_NAME: '18.\nGrantor company Corporation Tax reference, if applicable',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False},
                18: {RCKeys.COLUMN_NAME: '19.\nGrantor company PAYE reference',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: False},
                19: {RCKeys.COLUMN_NAME: '20.\nName of the company whose securities under option',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR120_TYPE, RCKeys.WARN_IF_BLANK: True},
                20: {RCKeys.COLUMN_NAME: '21.\nCompany whose securities under option – Address line 1',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: True},
                21: {RCKeys.COLUMN_NAME: '22.\nCompany whose securities under option – Address line 2',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                22: {RCKeys.COLUMN_NAME: '23.\nCompany whose securities under option – Address line 3',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                23: {RCKeys.COLUMN_NAME: '24.\nCompany whose securities under option – Address line 4',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                24: {RCKeys.COLUMN_NAME: '25.\nCompany whose securities under option – Country',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                25: {RCKeys.COLUMN_NAME: '26.\nCompany whose securities under option – Postcode',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR8_TYPE, RCKeys.WARN_IF_BLANK: False},
                26: {RCKeys.COLUMN_NAME: '27.\nCompany Reference Number (CRN) of company whose securities under option',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False},
                27: {RCKeys.COLUMN_NAME: '28.\nCorporation Tax reference of company whose securities under option',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.ensure_no_spaces},
                28: {RCKeys.COLUMN_NAME: '29.\nPAYE reference of company whose securities under option',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                29: {RCKeys.COLUMN_NAME: '30.\nWere the options exercised?\n(yes/no).\nIf yes go to next question\nIf no go to question 38',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                30: {RCKeys.COLUMN_NAME: '31.\nTotal number of securities employee entitled to on exercise of the option before any cashless exercise or other adjustment\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes},
                31: {RCKeys.COLUMN_NAME: '32.\nIf consideration was given for the securities, the amount given per security\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes},
                32: {RCKeys.COLUMN_NAME: '33.\nIf securities were acquired, Market Value (see note in guidance) of a security on the date of acquisition\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes},
                33: {RCKeys.COLUMN_NAME: '34.\nIf shares were acquired, are the shares listed on a recognised stock exchange?\n(yes/no).\nIf yes go to question 37\nIf no go to next question',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes_and_this_is_yes_no},
                34: {RCKeys.COLUMN_NAME: '35.\nIf shares were not listed on a recognised stock exchange, was valuation agreed with HMRC?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.no_35_special_validator},
                35: {RCKeys.COLUMN_NAME: '36.\nIf yes, enter the HMRC reference given',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_HMRC_ref},
                36: {RCKeys.COLUMN_NAME: '37.\nIf the shares were acquired,\ntotal deductible amount excluding\nany consideration given for the securities\n£\ne.g. 10.1234. Then go to question 40',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.no_37_special_validator},
                37: {RCKeys.COLUMN_NAME: '38.\nIf securities were not acquired, was money or value received on the release, assignment, cancellation or lapse of the option?\n(yes/no)\nIf yes go to next question\nIf no, no further information required on this event.',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                38: {RCKeys.COLUMN_NAME: '39.\nIf yes, amount of money or value received\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: False, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes},
                39: {RCKeys.COLUMN_NAME: '40.\nWas a NICs election or agreement operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                40: {RCKeys.COLUMN_NAME: '41.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                41: {RCKeys.COLUMN_NAME: '42.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_Acquisition_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM8_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nName of the company whose securities acquired',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR120_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nCompany whose securities acquired – Address line 1',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nCompany whose securities acquired – Address line 2',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                11: {RCKeys.COLUMN_NAME: '12.\nCompany whose securities acquired – Address line 3',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR27_TYPE, RCKeys.WARN_IF_BLANK: False},
                12: {RCKeys.COLUMN_NAME: '13.\nCompany whose securities acquired – Address line 4',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                13: {RCKeys.COLUMN_NAME: '14.\nCompany whose securities acquired – Country',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR18_TYPE, RCKeys.WARN_IF_BLANK: False},
                14: {RCKeys.COLUMN_NAME: '15.\nCompany whose securities acquired – Postcode',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR8_TYPE, RCKeys.WARN_IF_BLANK: False},
                15: {RCKeys.COLUMN_NAME: '16.\nCompany Reference Number (CRN) of company whose securities acquired',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False},
                16: {RCKeys.COLUMN_NAME: '17.\nCorporation Tax reference of company whose securities acquired',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: False},
                17: {RCKeys.COLUMN_NAME: '18.\nPAYE reference of company whose securities acquired',RCKeys.REQUIRED: False, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: False},
                18: {RCKeys.COLUMN_NAME: '19.\nDescription of security. Enter a number from 1 to 9. Follow the link in cell A7 for a list of security types',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUMBER_TYPE, RCKeys.WARN_IF_BLANK: True,RCKeys.SPECIAL_VALIDATOR: self.validate_between_1_and_9},
                19: {RCKeys.COLUMN_NAME: "20.\nIf the securities are not shares enter ' no' and go to question 24\nIf the securities are shares, are they part of the largest class of shares in the company?\n(yes/no)",RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                20: {RCKeys.COLUMN_NAME: '21.\nIf the securities are shares, are they listed on a recognised stock exchange?\n(yes/no)\nIf no go to question 22, If yes go to question 24',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes_and_this_is_yes_no},
                21: {RCKeys.COLUMN_NAME: '22.\nIf shares were not listed on a recognised stock exchange, was valuation agreed with HMRC?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_previous_yes_no_was_yes_and_this_was_no_or_yes_if_prev_no},
                22: {RCKeys.COLUMN_NAME: '23.\nIf yes, enter the HMRC reference given',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_HMRC_ref_Sheet_3},
                23: {RCKeys.COLUMN_NAME: '24.\nNumber of securities acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                24: {RCKeys.COLUMN_NAME: '25.\nSecurity type. Enter a number from 1 to 3, (follow the link at cell A7 for a list of security types).\nIf restricted go to next question.\nIf convertible go to question 32.\nIf both restricted and convertible enter 1 and answer all questions 26 to 32.\nIf neither restricted nor convertible go to question 29.',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUMBER_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_nature_of_restriction},
                25: {RCKeys.COLUMN_NAME: '26.\nIf restricted, nature of restriction. Enter a number from 1-3, follow the link at cell A7 for a list of restrictions',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUMBER_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_nature_of_restriction},
                26: {RCKeys.COLUMN_NAME: '27.\nIf restricted, length of time of restriction in years (if less than a whole year, enter as a decimal fraction, for example 0.6)', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM6V2_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_length_of_restriction},
                27: {RCKeys.COLUMN_NAME: '28.\nIf restricted, actual market value per security at date of acquisition\n£\ne.g. 10.1234\n(no entry should be made if an election to disregard ALL restrictions is operated)', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_restricted_market_val_per_security},
                28: {RCKeys.COLUMN_NAME: '29.\nUnrestricted market value per security at date of acquisition\n£\ne.g. 10.1234', RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_unrestricted_market_val_per_security},
                29: {RCKeys.COLUMN_NAME: '30.\nIf restricted, has an election been operated to disregard restrictions?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_election_happened_answer},
                30: {RCKeys.COLUMN_NAME: '31.\nIf an election has been operated to disregard restrictions, have all or some been disregarded?\n(enter all or some)' ,RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR4_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_some_or_all},
                31: {RCKeys.COLUMN_NAME: '32.\nIf convertible, market value per security ignoring conversion rights\n£\ne.g. 10.1234' ,RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_market_value_per_share_convertible},
                32: {RCKeys.COLUMN_NAME: '33.\nTotal price paid for the securities\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                33: {RCKeys.COLUMN_NAME: '34.\nWas the price paid in pounds sterling?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                34: {RCKeys.COLUMN_NAME: "35.\nWas there an artificial reduction in value on acquisition?\n(yes/no)\nIf 'yes' go to question 36, if 'No' go to question 37",RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                35: {RCKeys.COLUMN_NAME: '36.\nIf there was an artificial reduction in value, nature of the artificial reduction\nEnter a number from 1 to 3. Follow the link in cell A7 for a list of types of artificial restriction',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUMBER_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_nature_of_artifical_reduction},
                36: {RCKeys.COLUMN_NAME: '37.\nWere shares acquired under an employee shareholder arrangement?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                37: {RCKeys.COLUMN_NAME: '38.\nIf shares were acquired under an employee shareholder arrangement, was the total actual market value (AMV) of shares £2,000 or more?\n(yes/no)'},
                38: {RCKeys.COLUMN_NAME: '39.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                39: {RCKeys.COLUMN_NAME: '40.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_RestrictedSecurities_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM8_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance Number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nDate securities originally acquired\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nNumber of securities originally acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nFor disposals or lifting of restrictions, total chargeable amount\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME: '12.\nFor lifting of restrictions, are the shares listed on a recognised stock exchange?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                12: {RCKeys.COLUMN_NAME: '13.\nIf shares were not listed on a recognised stock exchange, was valuation agreed with HMRC?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_valuation_agreed_wtih_hmrc},
                13: {RCKeys.COLUMN_NAME: '14.\nIf yes, enter the HMRC reference given',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR10_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_hmrc_ref_given},
                14: {RCKeys.COLUMN_NAME: '15.\nFor variations, date of variation\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                15: {RCKeys.COLUMN_NAME: '16.\nFor variations, Actual Market Value (AMV) per security directly before variation\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                16: {RCKeys.COLUMN_NAME: '17.\nFor variations, Actual Market Value (AMV) per security directly after variation\n£\ne.g. 10.1234\n',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                16: {RCKeys.COLUMN_NAME: '18.\nHas a National Insurance Contribution election or agreement been operated (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                18: {RCKeys.COLUMN_NAME: '19.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                19: {RCKeys.COLUMN_NAME: '20.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_OtherBenefits_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nDate securities originally acquired\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nNumber of securities originally acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nAmount or market value of the benefit\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME: '12.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                12: {RCKeys.COLUMN_NAME: '13.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_Convertible_V3": {
                0: {RCKeys.COLUMN_NAME:'1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME:'2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME:'3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME:'4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME:'5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME:'6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME:'7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME:'8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME:'9.\nDate securities originally acquired\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME:'10.\nNumber of securities originally acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME:'11.\nFor receipt of money or value, enter amount or market value of the benefit\n£\ne.g. 10.1234\nThen go to question 14',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME:'12.\nFor conversion, disposal or release of entitlement to convert, total chargeable amount\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                12: {RCKeys.COLUMN_NAME:'13.\nHas a National Insurance Contribution election or agreement been operated (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                13: {RCKeys.COLUMN_NAME:'14.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                14: {RCKeys.COLUMN_NAME:'15.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK? (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_Notional_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nDate securities originally acquired\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nNumber of securities originally acquired\ne.g 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nAmount of notional loan discharged\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME: '12.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                12: {RCKeys.COLUMN_NAME: '13.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK? (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},

            },
            "Other_Enhancement_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nDate securities originally acquired\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nNumber of securities originally acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nTotal unrestricted market value (UMV) on 5th April or date of disposal if earlier\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME: '12.\nTotal UMV ignoring effect of artificial increase on date of taxable event\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                12: {RCKeys.COLUMN_NAME: '13.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                13: {RCKeys.COLUMN_NAME: '14.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK? (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            },
            "Other_Sold_V3": {
                0: {RCKeys.COLUMN_NAME: '1.\nDate of event\n(yyyy-mm-dd)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.DATE_TYPE, RCKeys.WARN_IF_BLANK: True},
                1: {RCKeys.COLUMN_NAME: '2.\nIs the event in relation to a disclosable tax avoidance scheme?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                2: {RCKeys.COLUMN_NAME: '3.\nIf yes, enter the eight-digit scheme reference number (SRN)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_srn},
                3: {RCKeys.COLUMN_NAME: '4.\nEmployee first name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                4: {RCKeys.COLUMN_NAME: '5.\nEmployee second name\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: False},
                5: {RCKeys.COLUMN_NAME: '6.\nEmployee last name',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR35_TYPE, RCKeys.WARN_IF_BLANK: True},
                6: {RCKeys.COLUMN_NAME: '7.\nNational Insurance number\n(if applicable)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR9_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_NINO},
                7: {RCKeys.COLUMN_NAME: '8.\nPAYE reference of employing company',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR14_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_paye_ref},
                8: {RCKeys.COLUMN_NAME: '9.\nNumber of securities originally acquired\ne.g. 100.00',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM11V2_TYPE, RCKeys.WARN_IF_BLANK: True},
                9: {RCKeys.COLUMN_NAME: '10.\nAmount received on disposal\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                10: {RCKeys.COLUMN_NAME: '11.\nTotal market value on disposal\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                11: {RCKeys.COLUMN_NAME: '12.\nExpenses incurred\n£\ne.g. 10.1234',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.NUM13V4_TYPE, RCKeys.WARN_IF_BLANK: True},
                12: {RCKeys.COLUMN_NAME: '13.\nWas PAYE operated?\n(yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
                13: {RCKeys.COLUMN_NAME: '14.\nWas any adjustment made for amounts subject to apportionment for residence or duties outside the UK? (yes/no)',RCKeys.REQUIRED: True, RCKeys.DATA_TYPE: ODS_Data_Types.CHAR3_TYPE, RCKeys.WARN_IF_BLANK: True, RCKeys.SPECIAL_VALIDATOR: self.validate_yes_no},
            }
        }
        # Column titles are stored in row 9 of the spreadsheets
        self.column_title_index = 8

    # =========================================================================
    # Custom validators
    # =========================================================================
    def no_35_special_validator(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        if row_data[current_index-1] == "yes":
            if len(str(row_data[current_index])) != 0:
                err_msg += f"Because 34 has been answered \"yes\" this value must be blank!"
        else:
            err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        return err_msg, warn_msg

    def no_37_special_validator(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        # Check that number 30 has been specified as yes
        err_msg = ''
        warn_msg = ''
        if row_data[29] == "yes":
            if len(str(row_data[current_index])) != 0:
                err_msg += f"Because \"30\" has been answered \"yes\" this value must be blank!"
        else:
            err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        return err_msg, warn_msg

    def validate_HMRC_ref(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        if row_data[33] == "yes":
            if len(str(row_data[current_index])) != 0:
                err_msg += f"Because \"34\" has been answered \"yes\" this value must be blank!"
        elif row_data[34] == "yes":
            err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        elif len(str(row_data[current_index])) != 0:
            err_msg += f"Because \"34\" or \"35\" not been answered \"yes\" this entry should be blank!"
        return err_msg, warn_msg

    def validate_HMRC_ref_Sheet_3(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        if row_data[21] == "no":
            if len(str(row_data[current_index])) != 0:
                err_msg += f"Because \"21\" has been answered \"no\" this value must be blank!"
        elif row_data[21] == "yes":
            err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        
        return err_msg, warn_msg

    def scheme_ref_num_validator(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''

        # Check the previous column for a value
        try:
            previous_cell_data = row_data[current_index-1]
            if previous_cell_data.lower() == "yes":
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        except Exception as e:
            print(f"ERRPR: {e}. {str(traceback.format_exc())}")
        return err_msg, warn_msg

    def validate_yes_no(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''

        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        if len(err_msg) == 0 and row_data[current_index] not in ["yes", "no"]:
            if row_data[current_index].lower() in ["yes", "no"]:
                err_msg += f"The cell contains {row_data[current_index]}, but the value is not all lower case!"
            else:
                err_msg += f"The cell contains {row_data[current_index]}, but the value must be \"yes\"\\\"no\"!"
        return err_msg, warn_msg

    def validate_NINO(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        nino_num = row_data[current_index]
        try:
            if type(nino_num) != str:
                raise TypeError
            length = len(nino_num)
            if length != 0:
                if ' ' in nino_num:
                    err_msg += f"The National Insurance Number contains a space character!"
                if length > 9:
                    err_msg += f"The National Insurance Number should be 9 characters but is {length}!"
            else:
                warn_msg += "The National Insurance Number is empty!"
        except TypeError as _:
            err_msg += f"The National Insurance Number must be a string!"
        except Exception as e:
            print(f"ERROR: {e}")
        return err_msg, warn_msg

    def validate_paye_ref(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        valid_numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        paye_data = row_data[current_index]
        for char in paye_data[0:3]:
            if char not in valid_numbers:
                err_msg += f"The PAYE entry does not start with three digits. Read value ({paye_data})!"
                break
        if paye_data[3] != "/":
            err_msg += f"The PAYE entry does is missing a forward slash after the first three digits. Read value ({paye_data})!"
        return err_msg, warn_msg

    def ensure_no_spaces(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''
        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], col_validator_data[RCKeys.WARN_IF_BLANK])
        try:
            if ' ' in row_data[current_index]:
                err_msg += f"The value should not contain spaces!"
        except Exception as e:
            print(f"ERROR: {e}")
        return err_msg, warn_msg

    def validate_previous_yes_no_was_yes(self, current_index, row_data, col_validator_data) -> typing.Tuple[list, list]:
        err_msg = ''
        warn_msg = ''

        # Check the previous values for a yes value
        try:
            for prev_col_value in row_data[current_index-1::-1]:
                if prev_col_value == "yes":
                    err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
                    break
            else:
                # Since no yes value was found, ensure this is empty
                if len(str(row_data[current_index])) > 0:
                    err_msg = "The value in this column was not empty and the previous switch column was not set to yes!"
        except Exception as e:
            print(f"Unexpected Error: {e}. {str(traceback.format_exc())}")
        return err_msg, warn_msg

    def validate_previous_yes_no_was_yes_and_this_is_yes_no(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''

        # Check the previous values for a yes value
        try:
            for prev_col_value in row_data[current_index-1::-1]:
                if prev_col_value == "yes":
                    err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
                    break
            else:
                # Since no yes value was found, ensure this is empty
                if len(str(row_data[current_index])) > 0:
                    err_msg = "The value in this column was not empty and the previous switch column was not set to yes!"
        except Exception as e:
            print(f"Unexpected Error: {e}. {str(traceback.format_exc())}")

        new_err_msg, new_warn_msg = self.validate_yes_no(current_index, row_data, col_validator_data)

        err_msg += new_err_msg
        warn_msg += new_warn_msg

        return err_msg, warn_msg

    def validate_srn(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if row_data[current_index-1] == "yes":
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif row_data[current_index] != '' and row_data[current_index] is not None:
                err_msg = f"The value should be blank since the previous column was not answered \"yes\""
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_between_1_and_9(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        try:
            val = int(row_data[current_index])
            if val < 1 or val > 9:
                err_msg = f"The entry must be a number greater than or equal to 1 and less than or equal to 9! Provided value was {val}"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_between_1_and_3(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        try:
            val = int(row_data[current_index])
            if val < 1 or val > 3:
                err_msg = f"The entry must be a number greater than or equal to 1 and less than or equal to 3! Provided value was {val}"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_nature_of_restriction(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        try:
            if row_data[current_index-1] != "" and row_data[current_index-1] is not None:
                prev_val = row_data[current_index-1]
                if type(prev_val) == int and prev_val == 1:
                    val = int(row_data[current_index])
                    if val < 1 or val > 3:
                        err_msg = f"The entry must be a number greater than or equal to 1 and less than or equal to 3! Provided value was {val}"
                elif len(str(row_data[current_index])) > 0:
                    err_msg = f"This entry should be left blank because the answer to \"25\" is not \"1\"!"
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"25 was left blank so this column should be blank!"                
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg


    def validate_previous_yes_no_was_yes_and_this_was_no_or_yes_if_prev_no(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if row_data[current_index-1] == "yes":
                # Make sure this row is blank
                if row_data[current_index] != '' or row_data[current_index] is not None:
                    err_msg = f"The previous yes/no column was answered \"yes\" so this entry should be blank"
            else:
                err_msg, warn_msg = self.validate_yes_no(self, current_index, row_data, col_validator_data)
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_length_of_restriction(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 1:
                # This value should be answered
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"1\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_restricted_market_val_per_security(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 1:
                # This value should be answered
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"1\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_unrestricted_market_val_per_security(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 2:
                # This value should be answered
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"2\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_election_happened_answer(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 1:
                # This value should be answered
                err_msg, warn_msg = self.validate_yes_no(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"1\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_some_or_all(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 1:
                # This value should be answered
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
                
                if row_data[current_index].strip().lower() not in ["all", "some"]:
                    err_msg += f"The contents of this entry should contain no additional whitespace!"
                elif row_data[current_index].lower() not in ["all", "some"]:
                    err_msg += f"The contents of this entry should be \"All\" or \"Some\""
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"1\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_market_value_per_share_convertible(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if type(row_data[24]) == int and row_data[24] == 3:
                # This value should be answered
                err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"25\" was not \"3\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_nature_of_artifical_reduction(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if str(row_data[34]).lower() == "yes":
                val = int(row_data[current_index])
                if val < 1 or val > 3:
                    err_msg = f"The entry must be a number greater than or equal to 1 and less than or equal to 3! Provided value was {val}"
                else:
                    # This value should be answered
                    err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
            elif len(str(row_data[current_index])) > 0:
                err_msg = f"This entry should be left blank because the answer to \"34\" was not \"yes\"!"
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_valuation_agreed_wtih_hmrc(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if str(row_data[11]).lower() == "yes":
                if len(str(row_data[current_index])) > 0:
                    err_msg =f"Because Number 12 has been answered yes, this column should be answered no."
                else:
                    err_msg, warn_msg = self.validate_yes_no(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    def validate_hmrc_ref_given(self, current_index, row_data, col_validator_data) -> typing.Tuple[str, str]:
        err_msg = ''
        warn_msg = ''
        try:
            if str(row_data[11]).lower() == "yes":
                if len(str(row_data[current_index])) > 0:
                    err_msg =f"Because Number 12 has been answered yes, this column should be answered no."
                else:
                    err_msg, warn_msg = self._check_data_type(row_data[current_index], col_validator_data[RCKeys.DATA_TYPE], True)
        except Exception as e:
            print(f"Unexpected error: {e}")
        return err_msg, warn_msg

    # =========================================================================
    # End custom validators
    # =========================================================================


    def validate_file(self, ods_file):
        if not isinstance(ods_file, ODS_File):
            raise TypeError(f"ERROR: The passed object was of type {type(ods_file)}, expected ODS_File!")
        # Retrieve all data from the sheet
        ods_file_data = ods_file.get_data()

        # 1) Validate the name and the position of the sheets
        try:
            err_msg_list = ''
            warn_msg_list = ''
            err_msg_list, warn_msg_list = self._validate_sheet_index_and_names(ods_file_data)
        except Exception as e:
            print(f"ERROR: Failed to validate the file data. {e} | {str(traceback.format_exc())}")

        ods_file.error_strings += err_msg_list
        ods_file.warning_strings += warn_msg_list

    def _validate_sheet_index_and_names(self, ods_file_data) -> typing.Tuple[list, list]:
        ods_file_sheets = [key for key in ods_file_data]
        error_msg_list = []
        warn_msg_list = []
        for index, sheet_name in enumerate(self.required_sheets):
            if sheet_name not in ods_file_sheets:
                error_msg_list.append(f"The sheet \"{sheet_name}\" is missing!")
            # Check the index
            if ods_file_sheets[index] != sheet_name:
                error_msg_list.append(f"The sheet \"{sheet_name}\" is not at the required index {index+1}!")

            # Validate the columns in this sheet
            erro_list, warn_list = self._validate_sheet_columns(sheet_name, ods_file_data[sheet_name])

            error_msg_list += erro_list
            warn_msg_list += warn_list

        return error_msg_list, warn_msg_list

    def _validate_sheet_columns(self, sheet_name, ods_sheet_data) -> typing.Tuple[list, list]:
        error_msg_list = []
        warn_msg_list = []
        required_columns = self.required_columns[sheet_name]
        # Row 9 contains the column names. 
        column_names = ods_sheet_data[self.column_title_index]

        for required_col_index, required_col_data in required_columns.items():
            try:
                required_col_name = required_col_data[RCKeys.COLUMN_NAME]
            except Exception as e:
                print(f"Unexpected error: {e}")
            try:
                # Check that the column name exists
                if required_col_name not in column_names:
                    error_msg_list.append(f"ERROR: Could not find the column ({required_col_name}) in the sheet ({sheet_name}). The found columns are ({column_names})")
                    # No further validation can be done since the column was not present
                    continue
            except Exception as e:
                print(f"Unexpected error: {e}")
            try:
                # Check that the column index is matched
                if column_names[required_col_index] != required_col_name:
                    error_msg_list.append(f"ERROR: The column ({required_col_name}) in the sheet ({sheet_name}) should be at index ({required_col_index}).")
                    # No further validation can be done since the column was not present
                    continue
            except Exception as e:
                print(f"Unexpected error: {e}")

        
        # Validate the data in all further rows
        for row_index, row_data in enumerate(ods_sheet_data[self.column_title_index+1:-1]):
            for column_index, column_data in enumerate(row_data):
                # Check the data type of the entry in the column
                if RCKeys.SPECIAL_VALIDATOR in required_columns[column_index]:
                    err_str, warn_str = required_columns[column_index][RCKeys.SPECIAL_VALIDATOR](column_index, row_data, required_columns[column_index])
                else:
                    err_str, warn_str = self._check_data_type(column_data, required_columns[column_index][RCKeys.DATA_TYPE], required_columns[column_index][RCKeys.WARN_IF_BLANK])
                if len(err_str) > 0:
                    column_text = f"{ODS_Column_Label_Lookup[column_index / 26] if column_index > 25 else ''}{ODS_Column_Label_Lookup[column_index % 26]}"
                    error_msg_list.append(f"ERROR: Sheet Name: {sheet_name}, Row: {row_index+self.column_title_index+2}, Column: {column_text}, Message: {err_str}")
                if len(warn_str) > 0:
                    column_text = f"{ODS_Column_Label_Lookup[column_index / 26] if column_index > 25 else ''}{ODS_Column_Label_Lookup[column_index % 26]}"
                    warn_msg_list.append(f"Warning: Sheet Name: {sheet_name}, Row: {row_index+self.column_title_index+2}, Column: {column_text}, Message: {warn_str}")
        
        return error_msg_list,warn_msg_list
            

    def _check_data_type(self, input_data, expected_type: ODS_Data_Types, warn_if_empty: bool) -> typing.Tuple[str, str]:
        err_string = ''
        warning_str = ''
        try:
            if expected_type == ODS_Data_Types.DATE_TYPE:
                # The input variable should have been parsed as a datetime object
                if type(input_data) != datetime:
                    # Invalid parse
                    raise TypeError()


            elif expected_type in ODS_Integer_Data_Types:
                # First check if it is empty
                if len(str(input_data)) == 0:
                    if warn_if_empty:
                        raise DataEmpty()
                    else:
                        # The cell is empty so no further validation needed
                        return

                if type(input_data) != int:
                    # Invalid parse
                    raise TypeError()
                # Check the length of the total character
                if len(str(input_data)) > ODS_Integer_Data_Types[expected_type]:
                    raise DataTooLong()

            elif expected_type in ODS_Float_Data_Types:
                # First check if it is empty
                if len(str(input_data)) == 0:
                    if warn_if_empty:
                        raise DataEmpty()
                    else:
                        # The cell is empty so no further validation needed
                        return
                # Check that the number is a float
                if type(input_data) != float:
                    raise TypeError()
                # Check that the total length is valid
                if len(str(input_data)) > ODS_Float_Data_Types[expected_type]["total"]:
                    raise DataTooLong()
                # Split the number into before and after the decimal
                before, after = str(input_data).split(".")
                if len(before) > ODS_Float_Data_Types[expected_type]["before"]:
                    raise BeforeDecimalTooLong
                if len(after) > ODS_Float_Data_Types[expected_type]["after"]:
                    raise AfterDecimalTooLong
                    
            elif expected_type in ODS_Char_Data_Types:
                # First check if it is empty
                if len(str(input_data)) == 0:
                    if warn_if_empty:
                        raise DataEmpty()
                    else:
                        # The cell is empty so no further validation needed
                        return
                # Check that the type is a string
                if type(input_data) != str:
                    raise TypeError()
                if len(input_data) > ODS_Char_Data_Types[expected_type]:
                    raise DataTooLong

        except TypeError as _:
            err_string = f"The data ({input_data!r}) is of type ({type(input_data)}) but the expected type is ({ODS_Data_Type_Strings[ODS_Data_Types.DATE_TYPE]})!"
        except DataTooLong as _:
            err_string = f"The data ({input_data!r}) is too long. It has a length of ({len(str(input_data))}) for the type ({ODS_Data_Type_Strings[ODS_Data_Types.DATE_TYPE]})!"
        except BeforeDecimalTooLong as _:
            err_string = f"The data ({input_data!r}) has too many digits before the decimal. It has a length of ({len(str(input_data).split('.')[0])}) for the type ({ODS_Data_Type_Strings[ODS_Data_Types.DATE_TYPE]})!"
        except AfterDecimalTooLong as _:
            err_string = f"The data ({input_data}) has too many digits after the decimal. It has a length of ({len(str(input_data).split('.')[1])}) for the type ({ODS_Data_Type_Strings[ODS_Data_Types.DATE_TYPE]})!"
        except DataEmpty as _:
            warning_str = f"The data was empty."
        except Exception as e:
            err_string = f"General error: {e}"
        
        return err_string, warning_str

