from ODS_COMMON.ods_constants import FILE_STATUS
import pyexcel_ods3 as ods_lib
import os

class ODS_File():
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_status = FILE_STATUS.FILE_STATUS_UNKNOWN
        self.error_strings = []
        self.warning_strings = []

        # Check that the file name is proper
        _, file_ext = os.path.splitext(self.file_name)
        if file_ext.lower() != ".ods":
            raise OSError(f"ERROR: Wrong file type ({file_ext}), needs to be *.ods")

    def get_data(self):
        return ods_lib.get_data(self.file_name)