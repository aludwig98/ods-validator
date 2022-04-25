import optparse
import os
from ODS_COMMON.ods_file import ODS_File
from ODS_COMMON.ods_validator import ODS_Validator
import csv

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--in", dest="input", type="string", help="The path to the file you would like to validate",
                      default="")
    parser.add_option("-o", "--out", dest="out", type="string", help="Directory to output the file to. This is just a path, the filename will be created automatically.",
                      default="")
    options, args = parser.parse_args()

    input_file = options.input.strip()
    output_dir = options.out.strip()

    if os.path.exists(input_file):
        file = ODS_File(input_file)
        validator = ODS_Validator()
        try:
            validator.validate_file(file)
        except Exception as e:
            print(f"Unknown Error: {e}")

        if output_dir is None or output_dir == "":
            output_dir = os.path.dirname(os.path.realpath(__file__))

        # Write the log files
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        error_log_path = os.path.join(output_dir, f"{os.path.basename(input_file)}_error_log.csv")
        with open(error_log_path, 'w', encoding='utf-8',newline='') as f:
            fieldnames = ['sheet_name', 'entry', 'row', 'column', 'message']
            error_csv_file = csv.DictWriter(f, fieldnames=fieldnames)
            error_csv_file.writeheader()
            error_csv_file.writerows(file.error_strings)
        # Warnings
        warning_log_path = os.path.join(output_dir, f"{os.path.basename(input_file)}_warning_log.csv")
        with open(warning_log_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['sheet_name', 'entry', 'row', 'column', 'message']
            warn_csv_file = csv.DictWriter(f, fieldnames=fieldnames)
            warn_csv_file.writeheader()
            warn_csv_file.writerows(file.warning_strings)
    else:
        print(f"The file {input_file} does not exist!")

    
        
