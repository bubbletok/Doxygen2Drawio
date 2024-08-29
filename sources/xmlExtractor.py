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

                # Convert the codeline's text to a single string, replacing <sp/> with spaces
                text = ' '.join([t if t != '<sp/>' else ' ' for t in codeline.itertext()])
                text = remove_attributes(text)  # Remove attributes such as [Range(...)], [SerializeField]

                if 'public' in text:
                    access_specifier = '+'
                elif 'protected' in text:
                    access_specifier = '#'
                else:
                    access_specifier = '-'
                
                if access_specifier not in {'+', '#', '-'}:
                    access_specifier = '?'  # Set a default value for unknown access specifiers

                # Check if it is a function or a variable
                if '(' in text or ')' in text:
                    function_signature = extract_function_signature(text)
                    extracted_info["member_functions"].append(f"{access_specifier} {function_signature}")
                else:
                    extracted_info["member_variables"].append(f"{access_specifier} {name}")

    return extracted_info

def remove_attributes(text):
    """
    Removes attributes like [Range(...)] and [SerializeField] from the code line text.
    
    Args:
    - text (str): The text containing attributes.
    
    Returns:
    - str: The text without attributes.
    """
    # Remove anything in square brackets
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

def extract_function_signature(text):
    match = re.search(r'\b(\w+[\w\s]*\w+)\s*\(([^)]*)\)', text)
    if match:
        function_name = match.group(1).strip()
        parameters = match.group(2).strip()
        parameters = re.sub(r'\[(.*?)\]', lambda m: '[' + m.group(1).replace(',', '') + ']', parameters)
        return f"{function_name}({parameters})"
    return text

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
    access_order = {'+': 1, '#': 2, '-': 3}

    sorted_functions = sorted(
        extracted_info["member_functions"], 
        key=lambda x: (access_order.get(x[0], 3), x)
    )
    sorted_variables = sorted(
        extracted_info["member_variables"], 
        key=lambda x: (access_order.get(x[0], 3), x)
    )

    return (sorted_functions, sorted_variables)

def create_text_file(file_name, text_content):
    try:
        with open(file_name, 'w') as file:
            file.write(text_content)
        print(f"File '{file_name}' created successfully.")
    except IOError as e:
        print(f"Error creating file '{file_name}': {e}")

def format_file_name(file_name):
    base_name = file_name.replace('.xml', '')
    formatted_name = re.sub(r'_(.)', lambda m: m.group(1).upper(), base_name)
    formatted_name = formatted_name.replace('8', '')
    formatted_name = formatted_name.replace('class', '')
    formatted_name = formatted_name.strip() + '.txt'
    return formatted_name

def clear_results_folder(folder_path):
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

if not os.path.exists(results_folder_path):
    os.makedirs(results_folder_path)
else:
    clear_results_folder(results_folder_path)

def Extract():
    all_extracted_info = parse_all_xml_in_folder(xml_folder_path)

    for file_info in all_extracted_info:
        xml_file_name = file_info['file_name']
        result_file_name = format_file_name(xml_file_name)

        txt_file_path = os.path.join(results_folder_path, result_file_name)

        content = ""
        content += f"Class Name: {file_info['extracted_info']['class_name']}\n"

        member_functions, member_variables = get_sorted_member_info(file_info['extracted_info'])

        content += "Member functions:\n"
        for _func in member_functions:
            content += _func + "\n"
        content += "Member variables:\n"
        for _var in member_variables:
            content += _var + "\n"

        print(content)
        create_text_file(txt_file_path, content)

if __name__ == '__main__':
    Extract()
