import os
import xml.etree.ElementTree as ET
import re

def parse_doxygen_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
        return None

    extracted_info = {
        "class_name": None,
        "member_functions": [],
        "member_variables": []
    }

    class_name_element = root.find(".//compoundname")
    if class_name_element is not None:
        extracted_info["class_name"] = class_name_element.text.strip()

    for codeline in root.findall(".//codeline"):
        refkind = codeline.get("refkind")
        if refkind == "member":
            ref_element = codeline.find(".//ref")
            if ref_element is not None:
                name = ref_element.text.strip()
                
                # Determine the access specifier
                access_specifier = ''
                text = ''.join(codeline.itertext())
                if 'public' in text:
                    access_specifier = '+'
                elif 'protected' in text:
                    access_specifier = '#'
                else:
                    access_specifier = '-'
                
                # Ensure that access_specifier is one of the valid keys
                if access_specifier not in {'+', '#', '-'}:
                    access_specifier = '?'  # Set a default value for unknown access specifiers

                # Check if it is a function or a variable
                if '(' in ''.join(codeline.itertext()) or ')' in ''.join(codeline.itertext()):
                    extracted_info["member_functions"].append(f"{access_specifier} {name}")
                else:
                    extracted_info["member_variables"].append(f"{access_specifier} {name}")

    return extracted_info

def parse_all_xml_in_folder(folder_path):
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith("cs.xml"):
            file_path = os.path.join(folder_path, filename)
            extracted_info = parse_doxygen_xml(file_path)
            if extracted_info is not None:
                results.append({
                    "file_name": filename,
                    "extracted_info": extracted_info
                })

    return results

def get_sorted_member_info(extracted_info):
    # Define the order of access specifiers
    access_order = {'+': 1, '#': 2, '-': 3}  # Add '?' for unknown access specifiers

    # Sort functions and variables by access specifier and then by name
    sorted_functions = sorted(
        extracted_info["member_functions"], 
        key=lambda x: (access_order.get(x[0], 3), x)  # Use get to handle unknown access specifiers
    )
    sorted_variables = sorted(
        extracted_info["member_variables"], 
        key=lambda x: (access_order.get(x[0], 3), x)  # Use get to handle unknown access specifiers
    )

    return (sorted_functions, sorted_variables)

def create_text_file(file_name, text_content):
    """
    Create a text file with the given name and write the provided content to it.

    Args:
    - file_name (str): The name of the file to be created.
    - text_content (str): The content to be written to the file, can be multiple lines.
    """
    try:
        with open(file_name, 'w') as file:
            file.write(text_content)
        print(f"File '{file_name}' created successfully.")
    except IOError as e:
        print(f"Error creating file '{file_name}': {e}")

def format_file_name(file_name):
    """
    Convert file name from 'name_with_underscores_and_8.xml' to 'NameWithUnderscoresAndTxt.txt'.
    Args:
    - file_name (str): The original file name.
    Returns:
    - str: The formatted file name.
    """
    base_name = file_name.replace('.xml', '')  # Remove .xml extension
    # Remove underscores and capitalize the next letter
    formatted_name = re.sub(r'_(.)', lambda m: m.group(1).upper(), base_name)
    # Remove all '8' characters
    formatted_name = formatted_name.replace('8', '')
    # Remove the substring "class"
    formatted_name = formatted_name.replace('class', '')
    # Strip leading/trailing whitespace and add .txt extension
    formatted_name = formatted_name.strip() + '.txt'
    return formatted_name

def clear_results_folder(folder_path):
    """
    Clear all files in the given folder.
    
    Args:
    - folder_path (str): The path of the folder to be cleared.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")

# Define the folder paths
xml_folder_path = os.path.join('xmls')
results_folder_path = os.path.join('texts')

# Ensure the results folder exists and clear it
if not os.path.exists(results_folder_path):
    os.makedirs(results_folder_path)
else:
    clear_results_folder(results_folder_path)

def Extract():
    # Example usage
    all_extracted_info = parse_all_xml_in_folder(xml_folder_path)

    for file_info in all_extracted_info:
        xml_file_name = file_info['file_name']
        result_file_name = format_file_name(xml_file_name)  # Format the file name

        # Create the path for the .txt file in the texts folder
        txt_file_path = os.path.join(results_folder_path, result_file_name)

        content = ""
        content += f"Class Name: {file_info['extracted_info']['class_name']}\n"

        member_functions = get_sorted_member_info(file_info['extracted_info'])[0]
        member_variables = get_sorted_member_info(file_info['extracted_info'])[1]

        content += "Member functions:\n"
        for _func in member_functions:
            content += _func
            content += "\n"
        content += "Member variables:\n"
        for _var in member_variables:
            content += _var
            content += "\n"

        print(content)
        create_text_file(txt_file_path, content)  # Use the modified file path

if __name__ == '__main__':
    Extract()