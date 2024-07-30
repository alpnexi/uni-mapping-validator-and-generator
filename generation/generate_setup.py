"""
This script generates mapper classes and updates the message type indicator mapping in a Java file.
"""

import os
import platform
from pathlib import Path
import pandas as pd
from termcolor import colored
from jinja2 import Environment, FileSystemLoader

# Constants for paths
if platform.system() == "Windows":
    BASE_DIR = Path("C:/Source/mapping-components-auth-trg")
else:
    BASE_DIR = Path("/Source/mapping-components-auth-trg")
COMMON_DIR = str(BASE_DIR / "mapping-components-auth-trg")
INBOUND_BASE_DIR = BASE_DIR / "mapping-components-auth-trg-dk-merchant"
INBOUND_MAPPERS_DIR_ISO_TO_UMM = INBOUND_BASE_DIR / "src/main/java/eu/nets/mapping/components/auth/trg/dk/merchant/iso8583_to_umm/message_mappers"
INBOUND_MAPPERS_DIR_UMM_TO_ISO = INBOUND_BASE_DIR / "src/main/java/eu/nets/mapping/components/auth/trg/dk/merchant/umm_to_iso8583/message_mappers"
OUTBOUND_BASE_DIR = BASE_DIR / "mapping-components-auth-trg-dk-merchant-nds"
OUTBOUND_MAPPERS_DIR_UMM_TO_ISO = OUTBOUND_BASE_DIR / "src/main/java/eu/nets/mapping/components/auth/trg/dk/merchant/nds/umm_to_iso8583/message_mappers"
OUTBOUND_MAPPERS_DIR_ISO_TO_UMM = OUTBOUND_BASE_DIR / "src/main/java/eu/nets/mapping/components/auth/trg/dk/merchant/nds/iso8583_to_umm/message_mappers"
dir_paths = {
    ("inbound", "iso_to_umm"): INBOUND_MAPPERS_DIR_ISO_TO_UMM,
    ("inbound", "umm_to_iso"): INBOUND_MAPPERS_DIR_UMM_TO_ISO,
    ("outbound", "iso_to_umm"): OUTBOUND_MAPPERS_DIR_ISO_TO_UMM,
    ("outbound", "umm_to_iso"): OUTBOUND_MAPPERS_DIR_UMM_TO_ISO,
}

environment = Environment(loader=FileSystemLoader("generation/templates/"))
INBOUND_ISO2UMM_TEMPLATE = environment.get_template("INBOUND_ISO2UMM_TEMPLATE.txt")
INBOUND_UMM2ISO_TEMPLATE = environment.get_template("INBOUND_UMM2ISO_TEMPLATE.txt")
OUTBOUND_UMM2ISO_TEMPLATE = environment.get_template("OUTBOUND_UMM2ISO_TEMPLATE.txt")
OUTBOUND_ISO2UMM_TEMPLATE = environment.get_template("OUTBOUND_ISO2UMM_TEMPLATE.txt")
templates = {
        ("inbound", "iso_to_umm"): INBOUND_ISO2UMM_TEMPLATE,
        ("inbound", "umm_to_iso"): INBOUND_UMM2ISO_TEMPLATE,
        ("outbound", "iso_to_umm"): OUTBOUND_ISO2UMM_TEMPLATE,
        ("outbound", "umm_to_iso"): OUTBOUND_UMM2ISO_TEMPLATE
}

def update_message_type_indicator(message_function, message_type_indicator):
    """
    Updates the message type indicator mapping in the Java file.

    Args:
        message_function (str): The message function.
        message_type_indicator (str): The message type indicator.

    Returns:
        None
    """
    # Read the Java file
    file_path = COMMON_DIR + "/src/main/java/eu/nets/mapping/components/auth/trg/common/message_function/MessageTypeIndicatorHelper.java"
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Prepare the mapping
    new_mapping = f'        map("{message_type_indicator}", MessageFunction.{message_function});\n'

    # Check for existing mapping
    mapping_exists = any(new_mapping.strip() in line for line in content)

    if not mapping_exists:
        insert_position = find_insertion_position(message_type_indicator, content)
        content.insert(insert_position, new_mapping)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(content)

        print("Mapping for " + colored(message_function, 'yellow') + " added successfully.")
    else:
        print("Mapping for " + colored(message_function, 'yellow') + " already exists. No changes needed.")

def find_insertion_position(message_type_indicator, content):
    """
    Finds the insertion position for the new mapping based on the message type indicator.

    Args:
        message_type_indicator (str): The message type indicator.
        content (list): The content of the Java file.

    Returns:
        int: The insertion position.
    """
    target_num = int(message_type_indicator)
    block_found = False
    insert_position = 0
    for i, line in enumerate(content):
        if 'map(' in line:
            try:
                # Extract the number from the line
                start = line.find('"') + 1
                end = line.find('"', start)
                number_str = line[start:end]

                # Convert to integer for comparison
                current_num = int(number_str)
                block_found = True

                # If the current number is greater than the target number, the position is found
                if current_num > target_num:
                    insert_position = i
                    return insert_position
            except ValueError:
                # Skip lines that do not contain valid numbers
                continue
        if '}' in line and block_found:
            # If the number is not found in the order, add the mapping before the closing brace at the end of the static block
            insert_position = i
            return insert_position
    return insert_position


def generate_mapper_class(message_function_description, message_function, direction, directional_conversion):
    """
    Generates a mapper class based on the provided parameters.

    Args:
        message_function_description (str): The description of the message function.
        message_function (str): The message function.
        direction (str): The direction of the mapper (inbound or outbound).
        birectional_conversion (str): The conversion type of the mapper (iso_to_umm or umm_to_iso).

    Returns:
        None
    """
    class_name = f"{message_function_description.replace(" ", "")}Mapper"

    template = templates[(direction, directional_conversion)]
    rendered = template.render(message_function=message_function, class_name=class_name)

    # Determine the correct directory based on direction
    dir_path = dir_paths[(direction, directional_conversion)]
    file_path = dir_path / f"{class_name}.java"

    # Check if the file already exists
    if os.path.exists(file_path):
        print("File " + colored({file_path}, 'yellow') + " already exists. Skipping generation to avoid overwriting.")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        print("Generated " + colored({file_path}, 'yellow') + "")

def handle_generation(message_function_description, message_function, directions_input):
    """
    Handles the generation process based on user input.

    Args:
        message_function_description (str): The description of the message function.
        message_function (str): The message function.
        directions_input (list): The directions needed for generation.

    Returns:
        None
    """
    directions_map = {
        "1": ("inbound", "iso_to_umm"),
        "2": ("inbound", "umm_to_iso"),
        "3": ("outbound", "umm_to_iso"),
        "4": ("outbound", "iso_to_umm")
    }

    for direction_key in directions_input:
        if direction_key in directions_map:
            direction, conversion = directions_map[direction_key]
            generate_mapper_class(message_function_description, message_function, direction, conversion)

def extract_variables_from_excel(file_path):
    """
    Extracts variables from an Excel file.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        tuple: A tuple containing the extracted values:
            - message_function (str): The extracted message function.
            - message_type_indicator (str): The extracted message type indicator.
    """
    # Read the Excel file
    df = pd.read_excel(file_path, header=None)

    # Find the column index for "ISO20022"
    iso_column_index = df.iloc[0].tolist().index('ISO20022')  # Adjust based on actual Excel layout
    target_row_index = 3  # For message_function, assuming it's still the same row

    # Extract message_function
    message_function_raw = df.iloc[target_row_index, iso_column_index]  # Adjust indices as necessary
    message_function = message_function_raw.split(", value ")[-1] if ", value " in message_function_raw else message_function_raw

    # Adjust logic for message_type_indicator
    # Find the cell with "Message Type Identifier" and then the cell to the right by 5 for its value
    message_type_identifier_location = df[df.applymap(lambda x: "Message Type Identifier" in str(x)).any(axis=1)].stack().index.tolist()[0]
    message_type_identifier_row, message_type_identifier_col = message_type_identifier_location
    message_type_indicator = df.iloc[message_type_identifier_row, message_type_identifier_col + 5]  # Adjust the column by +2 to find the value

    # Return the extracted values
    return message_function, message_type_indicator


def main():
    """
    The main function that executes the generation process.

    Returns:
        None
    """
    message_function, message_type_indicator = extract_variables_from_excel("Mapping_PSP to ISO20022_MTI12XX_V2.0.xlsx")
    message_function_description = "Financial Request"
    #message_function = "ADNO"
    #message_type_indicator = "1688"
    #message_function_description = input("Enter the message function description (e.g., Reversal Request): ")

    update_message_type_indicator(message_function, message_type_indicator)

    print(colored("1: inbound, iso to umm\n"
          "2: inbound, umm to iso\n"
          "3: outbound, umm to iso\n"
          "4: outbound, iso to umm", 'green'))
    directions_input = input(colored("Enter the directions needed (e.g., 1,3): ", 'green')).split(",")
    handle_generation(message_function_description, message_function, directions_input)

if __name__ == "__main__":
    main()