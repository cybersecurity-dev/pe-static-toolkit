
import math
import pefile
import os
import subprocess
import json
import hashlib
import pandas as pd
import time
import sys
import warnings

from datetime import datetime

warnings.filterwarnings('ignore')


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def shannon_entropy(data):
    # 256 different possible values
    possible = dict(((chr(x), 0) for x in range(0, 256)))

    for byte in data:
        possible[chr(byte)] += 1

    data_len = len(data)
    entropy = 0.0

    # compute
    for i in possible:
        if possible[i] == 0:
            continue

        p = float(possible[i] / data_len)
        entropy -= p * math.log(p, 2)
    return entropy

def import_table_list(indx, path, df):
    # if not is_exe(path):
    # pe = pefile.PE(path)
    # else:
    # return df
    ispe = "Yes"
    try:
        pe = pefile.PE(path)
    except pefile.PEFormatError:
        eprint("Not a PE")
        ispe = "No"
    if ispe != "No":
        try:
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                # print(entry.dll.decode('UTF-8'))
                lib_name = entry.dll.decode('UTF-8').lower()
                for imp in entry.imports:
                    func_name = imp.name.decode('UTF-8').lower()
                    # _txt = imp.name
                    # _txt.replace("b", "")
                    # _txt2 = _txt[0:-1]
                    # print(lib_name + '_' + func_name)
                    df.at[indx, lib_name + '_' + func_name] = int(1)
        except:
            df.at[indx, "import_table_list_succeeded"] = False
            return df
    # print(df)
    df.at[indx, "import_table_list_succeeded"] = True
    return df


def sections_entropy(indx, path, df):
    va = "_virtualaddress"
    vs = "_virtualsize"
    rs = "_rawsize"
    ey = "_entropy"

    ispe = "Yes"
    try:
        pe = pefile.PE(path)
    except pefile.PEFormatError:
        eprint("Not a PE")
        ispe = "No"
    if ispe != "No":
        try:
            for section in pe.sections:
                section_name = section.Name.decode('utf-8')[1:].lower()
                df.at[indx, section_name + va] = hex(section.VirtualAddress)
                df.at[indx, section_name + vs] = hex(section.Misc_VirtualSize)
                df.at[indx, section_name + rs] = hex(section.SizeOfRawData)
                df.at[indx, section_name + ey] = str(shannon_entropy(section.get_data()))

                # print("\tvirtual address: " + hex(section.VirtualAddress))
                # print("\tvirtual size: " + hex(section.Misc_VirtualSize))
                # print("\traw size: " + hex(section.SizeOfRawData))
                # print("\tentropy: " + str(shannon_entropy(section.get_data())))
        except:
            df.at[indx, "sections_entropy_succeeded"] = False
            return df
    df.at[indx, "sections_entropy_succeeded"] = True
    return df


def run_exiftool(json_output_dir, full_file_path, file_sha256, df, indx):
    full_json_output_path = json_output_dir + file_sha256 + ".json"
    if not os.path.exists(full_json_output_path):
        with open(full_json_output_path, "w") as json_file:
            exiftool_command = ["exiftool", "-json", full_file_path]
            subprocess.run(exiftool_command, stdout=json_file)
    else:
        print("Already exported: -" + file_sha256 + '-')

    try:
        json_file = open(full_json_output_path)
        json_data = json.load(json_file)[0]
    except:
        eprint("An exception occurred for file hash:", file_sha256)
        eprint(full_json_output_path)
        eprint()
        df.at[indx, 'exiftool_succeeded'] = False
        return
        # if "FileName" in json_data:
        # df.at[indx, 'filename'] = json_data['FileName']
    # if "Directory" in json_data:
    # df.at[indx, 'directory'] = json_data['Directory']
    if "FileSize" in json_data:
        df.at[indx, 'file_size'] = json_data['FileSize']
    if "FileModifyDate" in json_data:
        df.at[indx, 'filemodify_date'] = json_data['FileModifyDate']
    if "FileAccessDate" in json_data:
        df.at[indx, 'file_access_date'] = json_data['FileAccessDate']
    if "FileInodeChangeDate" in json_data:
        df.at[indx, 'file_inode_change_date'] = json_data['FileInodeChangeDate']
    if "FilePermissions" in json_data:
        df.at[indx, 'file_permissions'] = json_data['FilePermissions']
    if "FileType" in json_data:
        df.at[indx, 'filetype'] = json_data['FileType']
    if "FileTypeExtension" in json_data:
        df.at[indx, 'file_type_extension'] = json_data['FileTypeExtension']
    if "MIMEType" in json_data:
        df.at[indx, 'mimetype'] = json_data['MIMEType']
    if "MachineType" in json_data:
        df.at[indx, 'machine_type'] = json_data['MachineType']
    if "TimeStamp" in json_data:
        df.at[indx, 'timestamp'] = json_data['TimeStamp']
    if "ImageFileCharacteristics" in json_data:
        df.at[indx, 'image_file_characteristics'] = json_data['ImageFileCharacteristics']
    if "PEType" in json_data:
        df.at[indx, 'petype'] = json_data['PEType']
    if "LinkerVersion" in json_data:
        df.at[indx, 'linker_version'] = json_data['LinkerVersion']
    if "CodeSize" in json_data:
        df.at[indx, 'code_size'] = json_data['CodeSize']
    if "InitializedDataSize" in json_data:
        df.at[indx, 'initialized_data_size'] = json_data['InitializedDataSize']
    if "UninitializedDataSize" in json_data:
        df.at[indx, 'uninitialized_data_size'] = json_data['UninitializedDataSize']
    if "EntryPoint" in json_data:
        df.at[indx, 'entrypoint'] = json_data['EntryPoint']
    if "OSVersion" in json_data:
        df.at[indx, 'directory'] = json_data['OSVersion']
    if "ImageVersion" in json_data:
        df.at[indx, 'os_version'] = json_data['ImageVersion']
    if "SubsystemVersion" in json_data:
        df.at[indx, 'subsystem_version'] = json_data['SubsystemVersion']
    if "Subsystem" in json_data:
        df.at[indx, 'subsystem'] = json_data['Subsystem']
    if "FileVersionNumber" in json_data:
        df.at[indx, 'file_version_number'] = json_data['FileVersionNumber']
    if "ProductVersionNumber" in json_data:
        df.at[indx, 'product_version_number'] = json_data['ProductVersionNumber']
    if "FileFlagsMask" in json_data:
        df.at[indx, 'file_flags_mask'] = json_data['FileFlagsMask']
    if "FileFlags" in json_data:
        df.at[indx, 'file_flags'] = json_data['FileFlags']
    if "FileOS" in json_data:
        df.at[indx, 'file_os'] = json_data['FileOS']
    if "ObjectFileType" in json_data:
        df.at[indx, 'object_file_type'] = json_data['ObjectFileType']
    if "FileSubtype" in json_data:
        df.at[indx, 'file_subtype'] = json_data['FileSubtype']
    if "LanguageCode" in json_data:
        df.at[indx, 'language_code'] = json_data['LanguageCode']
    if "CharacterSet" in json_data:
        df.at[indx, 'character_set'] = json_data['CharacterSet']
    if "FileDescription" in json_data:
        df.at[indx, 'file_description'] = json_data['FileDescription']
    if "FileVersion" in json_data:
        df.at[indx, 'file_version'] = json_data['FileVersion']
    if "InternalName" in json_data:
        df.at[indx, 'internal_name'] = json_data['InternalName']
    if "LegalCopyright" in json_data:
        df.at[indx, 'legal_copyright'] = json_data['LegalCopyright']
    if "OriginalFileName" in json_data:
        df.at[indx, 'original_file_name'] = json_data['OriginalFileName']
    if "ProductName" in json_data:
        df.at[indx, 'product_name'] = json_data['ProductName']
    if "ProductVersion" in json_data:
        df.at[indx, 'product_version'] = json_data['ProductVersion']
    if "SquirrelAwareVersion" in json_data:
        df.at[indx, 'squirrel_aware_version'] = json_data['SquirrelAwareVersion']
    if "CompanyName" in json_data:
        df.at[indx, 'company_name'] = json_data['CompanyName']
        # _filename = os.path.splitext(_file)[0]
        # print(_filename)
    df.at[indx, 'exiftool_succeeded'] = True
    json_file.close()


def pe_extractor_runner(exe_dir, json_output_dir):
    # hash_list = []
    indx = 0
    df = pd.DataFrame()
    flag = False
    # extensions = ("exe", "Exe", "EXE", "msi", "Dll", "DLL")
    extensions = ("exe", "Exe", "EXE", "msi", "Dll", "DLL", "dll")

    for r, d, f in os.walk(exe_dir):
        for filename in f:
            if not filename.endswith(extensions):
                eprint("this file is not executable: ", filename)
                continue
            else:
                # print(filename)
                # print("Index:", indx)
                df_import = pd.DataFrame()
                df_section = pd.DataFrame()
                full_file_path = os.path.join(r, filename)
                # print(os.path.join(r, file))
                sha256_hash = hashlib.sha256()
                with open(full_file_path, "rb") as f:
                    # Read and update hash string value in blocks of 4K
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                # print(sha256_hash.hexdigest())
                # hash_list.append(sha256_hash.hexdigest())
                df.at[indx, 'sha256_hash'] = sha256_hash.hexdigest()
                print("-------------------------------------------------------------------")
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                print("File operation started at: ", date_time)
                print("Next hash file::", df.at[indx, 'sha256_hash'])
                print("Full_file_path::", full_file_path)
                print("-------------------------------------------------------------------")
                if indx % 100 == 0:
                    print("Hundred Element Count:", indx)
                sections_entropy(indx, full_file_path, df)
                import_table_list(indx, full_file_path, df)
                run_exiftool(json_output_dir, full_file_path, sha256_hash.hexdigest(), df, indx)
                df.at[indx, 'label'] = int(0)
                indx = indx + 1
                # import_table_list(indx, os.path.join(r, filename), df_import)
                # sections_entropy(indx, os.path.join(r, filename), df_section)
                # df_section_import = pd.concat([df_import, df_section], ignore_index=True, sort=False)
                # df_section_import.to_json(sha256_hash.hexdigest() + '.json')
        if flag:
            break
    #print(df.shape)
    return df


def main(exe_dir, json_output_dir):
    eprint("----------Benign_Metadata_Extractor_From_Files.err----------START----------")
    
    df_new = pe_extractor_runner(exe_dir, json_output_dir)
    print("PE_EXTRACTOR_RUNNER function is finished")
    #df_new.shape

    today = datetime.today()
    todayDate = today.strftime("%d_%m_%Y")
    file_name = "benign_metadata_none_" + todayDate
    file_type = ".pkl"

    df_new.to_pickle(file_name + file_type)  # save
    print(file_name + ".pkl file is created")
    #print(df_new)

    df_removeduplicates = df_new.drop_duplicates(subset='sha256_hash', keep="first")
    #print(df_deletedduplicate["label"].value_counts())
    #print(df_new)

    row_count_diff = len(df_new) - len(df_removeduplicates)
    print("Deleted duplicated rows count:", row_count_diff)


    df_removeduplicates.to_pickle(file_name  + "_rmduplicated" + file_type)  # save
    print(file_name  + "_rmduplicated" + file_type + " file is created")

    eprint("----------Benign_Metadata_Extractor_From_Files.err---------- END ----------")

if __name__ == "__main__":
    print("[" + __file__ + "]'s last modified: %s" % time.ctime(os.path.getmtime(__file__)))
    # Check if a parameter is provided
    if len(sys.argv) == 3:
        in_dir = sys.argv[1]
        if not os.path.exists(in_dir):
            print(f"Directory: '{in_dir}' does not exist.")
            exit()
        print(f"\n\nExe Directory:\t\t{in_dir}")

        out_dir = sys.argv[2]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        print(f"JSON Files will save:\t{out_dir}")
        main(in_dir, out_dir)
    else:
        print("No input directory and output directory provided.")
