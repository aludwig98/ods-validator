import optparse
import os
from ODS_COMMON.ods_file import ODS_File
from ODS_COMMON.ods_validator import ODS_Validator

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-i", "--in", dest="_in_", type="string", help="The path to the file you would like to validate",
                      default="")
    parser.add_option("-o", "--out", dest="out", type="string", help="Directory to output the file to. This is just a path, the filename will be created automatically.",
                      default="")
    options, args = parser.parse_args()

    input_file = options._in_.strip()
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
        error_log_path = os.path.join(output_dir, "error_log.txt")
        with open(error_log_path, 'w') as f:
            for error in file.error_strings:
                f.write(error)
                f.write("\n")
        warning_log_path = os.path.join(output_dir, "warning_log.txt")
        with open(warning_log_path, 'w') as f:
            for warn in file.warning_strings:
                f.write(warn)
                f.write("\n")
    else:
        print(f"The file {input_file} does not exist!")

    
        
