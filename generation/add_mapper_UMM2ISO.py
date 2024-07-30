import os, re
import platform
import generate_setup as setup
from pathlib import Path
from termcolor import colored
from jinja2 import Environment, FileSystemLoader

# Constants for paths
# Constants for paths
if platform.system() == "Windows":
    BASE_DIR = "C:/Source/mapping-components-auth-trg"
else:
    BASE_DIR = "/Source/mapping-components-auth-trg"
COMMON_DIR = BASE_DIR + "/mapping-components-auth-trg"
MAIN_JAVA = "/src/main/java/"
FIELD_MAPPERS_PATH_UMM_TO_ISO = "eu/nets/mapping/components/auth/trg/umm_to_iso8583/field_mappers"
FIELD_MAPPERS_DIR_UMM_TO_ISO = COMMON_DIR + MAIN_JAVA + FIELD_MAPPERS_PATH_UMM_TO_ISO
FIELD_MAPPERS_PATH_ISO_TO_UMM = "eu/nets/mapping/components/auth/trg/iso8583_to_umm/field_mappers"
FIELD_MAPPERS_DIR_ISO_TO_UMM = COMMON_DIR + MAIN_JAVA + FIELD_MAPPERS_PATH_ISO_TO_UMM
INBOUND_BASE_DIR = BASE_DIR + "/mapping-components-auth-trg-dk-merchant"
INBOUND_MAPPERS_DIR_ISO_TO_UMM = INBOUND_BASE_DIR + MAIN_JAVA + "eu/nets/mapping/components/auth/trg/dk/merchant/iso8583_to_umm/message_mappers"
INBOUND_MAPPERS_DIR_UMM_TO_ISO = INBOUND_BASE_DIR + MAIN_JAVA + "eu/nets/mapping/components/auth/trg/dk/merchant/umm_to_iso8583/message_mappers"
OUTBOUND_BASE_DIR = BASE_DIR + "/mapping-components-auth-trg-dk-merchant-nds"
OUTBOUND_MAPPERS_DIR_UMM_TO_ISO = OUTBOUND_BASE_DIR + MAIN_JAVA + "eu/nets/mapping/components/auth/trg/dk/merchant/nds/umm_to_iso8583/message_mappers"
OUTBOUND_MAPPERS_DIR_ISO_TO_UMM = OUTBOUND_BASE_DIR + MAIN_JAVA + "eu/nets/mapping/components/auth/trg/dk/merchant/nds/iso8583_to_umm/message_mappers"
dir_paths = {
    ("inbound", "iso_to_umm"): INBOUND_MAPPERS_DIR_ISO_TO_UMM,
    ("inbound", "umm_to_iso"): INBOUND_MAPPERS_DIR_UMM_TO_ISO,
    ("outbound", "iso_to_umm"): OUTBOUND_MAPPERS_DIR_ISO_TO_UMM,
    ("outbound", "umm_to_iso"): OUTBOUND_MAPPERS_DIR_UMM_TO_ISO,
}
    
# Function to analyze a message mapper
def analyze_message_mapper(message_mapper_path, field):
    # Read the message mapper file
    message_mapper_content = read_file(message_mapper_path)
    
    # Analyze the mapper content (e.g., check implemented fields)
    field_implemented = analyze_mapper_content(message_mapper_content, field)
    return field_implemented

# Function to check and modify DataElementMapperDelegator for a specific field
def modify_message_mapper(message_mapper_path, field):
    field_mapper = locate_field_mapper(field)

    # Read the message mapper file
    message_mapper_content = read_file_as_string(message_mapper_path)
    
    # Check if the field is already implemented
    modified_content = add_field_to_delegator(message_mapper_content, field_mapper)
        
    # Write the modified content back to the file
    write_file(message_mapper_path, modified_content)


# Function to find the field mapper for a specific field and implement it if it doesn't exist
def locate_field_mapper(field):
    possible_field_mappers = does_field_mapper_exist(field, "umm_to_iso")
    if possible_field_mappers.__len__() == 0:
        implement_new_mapper(field)
    else:
        index = 1
        if possible_field_mappers.__len__() > 1:
            print(colored(f"Found different options for the field mappers for field {field}, please select which one to use:", 'yellow'))
            for i, mapper in enumerate(possible_field_mappers):
                print(colored(f"{i+1}. {mapper}", 'yellow'))
            index = int(input("Enter the number of the field mapper to use: "))
            while index < 1 or index > len(possible_field_mappers):
                print(colored("Invalid input. Please enter a valid number.", 'red'))
                index = int(input("Enter the number of the field mapper to use: "))
        return possible_field_mappers[index-1]


# Function to construct message mapper path based on description and direction
def locate_message_mapper(message_function, message_function_description, direction, bidirection):
    # Logic to construct the path based on project structure and inputs
    mapper_name = f"{message_function_description.replace(' ', '')}Mapper"
    
    # Find the directory path based on direction and bidirection
    dir_path = dir_paths.get((direction, bidirection))
    
    if dir_path is None:
        raise ValueError("Invalid direction or bidirection provided.")
    
    # Construct the full path to the mapper
    full_path = dir_path + "/" +  mapper_name + ".java"
    
    # Check if the mapper exists under the constructed path
    if os.path.exists(full_path):
        print(f"Message mapper found: " + colored(full_path, 'yellow'))
    else:
        print(f"Message mapper not found: " + colored(full_path, 'yellow') + ", generating on the spot")
        setup.generate_mapper_class(message_function_description, message_function, direction, bidirection)

    return full_path

# Function to read a file line by line
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

# Function that reads the entire file into a single string
def read_file_as_string(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Function to analyze mapper content to find implemented fields
def analyze_mapper_content(content, field):
    # Pattern to match field mapper calls, e.g., .de2_PrimaryAccountNumberMapper(DE2_PrimaryAccountNumber())
    field_mapper_pattern = re.compile(r'\.de(\d+)_([A-Za-z0-9]+)\(')

    field_found = False

    # Iterate through each line of the content
    for line in content:
        # Search for the pattern in the current line
        match = field_mapper_pattern.search(line)
        if match:
            # Extract field number and mapper name
            field_number = match.group(1)
            mapper_name = match.group(2)

            # Check if the specific field is being searched for, if so, add it to the list
            if field == int(field_number) or field == "all":
                field_found = True
                break

    return field_found

# Function to check if a specific field mapper implementation exists in the path 
def does_field_mapper_exist(field, direction):    
    # Pattern to match files, e.g., DE49_TransactionCurrencyCodeMapper
    file_pattern = re.compile(rf'DE{field}_\w+Mapper\.java$')
    possible_field_mappers = []
    if direction == "umm_to_iso": 
        directory = FIELD_MAPPERS_DIR_UMM_TO_ISO
        for filename in os.listdir(directory):
            # Check if the filename matches the pattern
            if file_pattern.match(filename):
                possible_field_mappers.append(filename)
    if possible_field_mappers.__len__() == 0:
        print(f"Field mapper for field {field} is not implemented.")
    return possible_field_mappers

# Function to add a new field to the DataElementMapperDelegator
def add_field_to_delegator(content, field_mapper):

    # Step 1: Identify the builder method call start and end
    builder_start = content.find("DataElementMapperDelegator.<UniMessageContext, MappingContext>builder()")
    builder_end = content.find(".build()", builder_start) + len(".build()")
    
    # Extract the builder method content
    builder_content = content[builder_start:builder_end]
    
    # Find all existing field numbers in the builder content
    existing_fields = re.findall(r"\.de(\d+)", builder_content)
    existing_fields_numbers = [int(num) for num in existing_fields]
    
    # Determine the correct insertion point based on field number
    new_field_number = get_de_number(field_mapper)
    insertion_index = None
    for i, num in enumerate(existing_fields_numbers):
        if new_field_number < num:
            # Find the position of the field just larger than the new field
            insertion_index = builder_content.find(f".de{num}")
            break
    
    # If the new field number is larger than any existing, append before .build()
    if insertion_index is None:
        insertion_index = builder_content.rfind(".build()")
    
    instance_call = create_instance_call_line(field_mapper)

    field_method = field_mapper.replace(".java", "").split("_")[-1]
    # Construct the new field method call
    new_field_method_call = f".de{new_field_number}_{field_method}({instance_call})\n                        "
    
    # Construct the static import line
    static_import_line = create_static_import_line(field_mapper, FIELD_MAPPERS_PATH_UMM_TO_ISO) + "\n"
    # Find the position package declaration
    position_after_second_newline = content.find('\n', content.find('\n') + 1) + 1
    content_with_imports = content[:position_after_second_newline] + static_import_line + content[position_after_second_newline:builder_start]

    # Insert the new field method call into the builder content
    modified_builder_content = builder_content[:insertion_index] + new_field_method_call + builder_content[insertion_index:]

    # Replace the old builder content in the original content with the modified one
    modified_content = content_with_imports + modified_builder_content + content[builder_end:]
    
    return modified_content

def create_instance_call_line(field_mapper):
    # Find the field mapper class name
    field_mapper_class_name = field_mapper.split(".")[0]
    
    directory = FIELD_MAPPERS_DIR_UMM_TO_ISO + "/" + field_mapper_class_name + ".java"
    # Find the instance call for the field mapper
    field_mapper_instance_call = find_field_mapper_instance_call(field_mapper_class_name, directory)
    return field_mapper_instance_call

def find_field_mapper_instance_call(class_name, directory):
    # Read the field mapper class file
    class_content = read_file_as_string(directory)

    # Regex pattern to find "public static {className}" followed by any method call
    pattern = rf"public static {class_name}\s+([^\s(]+)\s*\("
    
    match = re.search(pattern, class_content)
    
    if match:
        # Return the method call found
        return match.group(1) + "()"
    else:
        raise ValueError(f"Instance call not found for class {class_name}")
    
def create_static_import_line(field_mapper_path, field_mapper_dir):
    # Extract the package path from the field mapper directory
    package_path = field_mapper_dir.replace("/", ".").strip(".")

    # Extract the class name and field name from the file name
    class_name = field_mapper_path.split("/")[-1].replace(".java", "")
    field_name = class_name.replace("Mapper", "")

    # Construct the static import line
    import_line = f"import static {package_path}.{class_name}.{field_name};"

    return import_line

def get_de_number(filename):
    # Regex pattern to match "DE" followed by any number of digits
    pattern = r"DE(\d+)_"
    
    # Search for the pattern in the filename
    match = re.search(pattern, filename)
    
    if match:
        # Return the number part as an integer
        return int(match.group(1))
    else:
        return None
        
# Function to write modified content back to a file
def write_file(file_path, content):
    with open(file_path, 'w') as file:   
        file.writelines(content)

# Function to implement a new mapper based on specifications
def implement_new_mapper(field):
    # Logic to create and save a new mapper implementation
    print(colored("Field mapper not implemented. Function needs to be implemented", 'red'))
    raise RuntimeError("Field mapper not implemented. Function needs to be implemented")


def main():
    message_function = "RVRA" #"ADNO" 
    message_function_description = "Reversal Advice" #"Addendum Notification" 
    directions = ["inbound", "outbound"]
    bidirection = "umm_to_iso"
    
    for i, dir in enumerate(directions):
        print(colored(f"{i+1}. {dir}", 'yellow'))
    index = int(input(colored("Enter the number of the direction to use: ", 'white'))) 
    while index < 1 or index > len(directions):
        print(colored("Invalid direction number. Please enter a valid number.", 'red'))
        index = int(input(colored("Enter the number of the direction to use: ", 'white'))) 
    direction = directions[index-1]
    
    field = int(input(colored("Enter the field number to implement: ", 'white'))) 
    message_mapper_path = locate_message_mapper(message_function, message_function_description, direction, bidirection)
    field_implemented = analyze_message_mapper(message_mapper_path, field)

    if field_implemented:
        print(colored(f"Field {field} is already implemented in the message mapper.", "green"))
    else:
        print(colored(f"Field {field} is not implemented in the message mapper.", "red"))
        modify_message_mapper(message_mapper_path, field)
        print(colored(f"Field {field} has been successfully implemented in the message mapper.", "green"))
    print(colored("Process completed.", "green"))    

if __name__ == "__main__":
    main()