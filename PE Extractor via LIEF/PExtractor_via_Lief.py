import lief

# Extract header information
def extract_header_info(pe):
    print("************DOS HEADER INFORMATION************")
    print(f"Magic: {pe.dos_header.magic}")
    
    print("************HEADER INFORMATION************")
    print(f"File type: {pe.header.machine}")
    print(f"Time Date Stamp: {pe.header.time_date_stamps}")
    print(f"Entry point: {hex(pe.optional_header.addressof_entrypoint)}")
    print(f"Image base: {hex(pe.optional_header.imagebase)}")
    print(f"Subsystem: {pe.optional_header.subsystem}")
    print(f"Number of sections: {pe.header.numberof_sections}")

    
    print("************DETAILED HEADER INFORMATION************")
    # Check if the PE is 32-bit (PE32) or 64-bit (PE32+)
    if pe.optional_header.magic == lief.PE.PE_TYPE.PE32_PLUS:
        pe_format = "PE32+ (64-bit)"
    else:
        pe_format = "PE32 (32-bit)"
    
    print(f"PE Format: {pe_format}")
    print(f"Machine Type: {pe.header.machine}")
    print(f"Number of Sections: {pe.header.numberof_sections}")
    print(f"Time Date Stamp: {pe.header.time_date_stamps}")
    print(f"Pointer to Symbol Table: {pe.header.pointerto_symbol_table}")

    print("\n************OPTIONAL HEADER INFORMATION************")
    print(f"Section Alignment: {pe.optional_header.section_alignment}")
    print(f"File Alignment: {pe.optional_header.file_alignment}")
    print(f"Major Operating System Version: {pe.optional_header.major_operating_system_version}")
    print(f"Minor Operating System Version: {pe.optional_header.minor_operating_system_version}")
    print(f"Major Image Version: {pe.optional_header.major_image_version}")
    print(f"Minor Image Version: {pe.optional_header.minor_image_version}")
    print(f"Size of Headers: {pe.optional_header.sizeof_headers}")
    print(f"CheckSum: {pe.optional_header.checksum}")    


# Extract import table information
def extract_import_table(pe):
    print("\n************IMPORT TABLE************")
    for import_entry in pe.imports:
        print(f"Imported DLL: {import_entry.name}")
        for function in import_entry.entries:
            func_name = function.name if function.name else f"Ordinal: {function.ordinal}"
            print(f"\tFunction: {func_name}")
            strImportedDllFunction = import_entry.name + "_" + func_name
            #print(strImportedDllFunction)


# Extract export table information
def extract_export_table(pe):
    print("\n************EXPORT TABLE************")
    if pe.has_exports:
        print(f"Exported DLL: {pe.name}")
        for export_entry in pe.get_export().entries:
            func_name = export_entry.name if export_entry.name else f"Ordinal: {export_entry.ordinal}"
            print(f"\tExported Function: {func_name}")
            strExportedDllFunction = import_entry.name + "_" + func_name
            #print(strExportedDllFunction)
    else:
        print("No exports found")

# Load the PE file
pe_file_path = "SlackSetup.exe"
pe = lief.parse(pe_file_path)


extract_header_info(pe)
extract_import_table(pe)
extract_export_table(pe)