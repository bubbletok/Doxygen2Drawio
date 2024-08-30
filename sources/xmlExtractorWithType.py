import os
import xml.etree.ElementTree as ET
import re

def extract_type_info(text):
    """
    함수 시그니처에서 반환형만 추출합니다.
    """
    # 접근 지정자와 기타 키워드를 제거한 후
    # 반환형을 찾습니다.
    
    # 접근 지정자 제거
    text = re.sub(r'\b(public|protected|private|static|override|virtual|abstract)\b', '', text).strip()
    # print(text)
    
    # 함수 시그니처의 시작 부분에서 반환형을 추출
    # 반환형은 첫 번째 단어로 가정
    match = re.match(r'^\b(?:\w+|void)\b', text)
    
    if match:
        return match.group(0)
    return 'void'


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
                # Extract the full text for the current codeline

                # Convert the codeline's text to a single string, replacing <sp/> with spaces
                text = ' '.join([t if t != '<sp/>' else ' ' for t in codeline.itertext()])
                text = remove_attributes(text)  # Remove attributes such as [Range(...)], [SerializeField]

                # Determine the access specifier
                access_specifier = ''
                if 'public' in text:
                    access_specifier = '+'
                elif 'protected' in text:
                    access_specifier = '#'
                else:
                    access_specifier = '-'

                #print(text)
                # Extract the type information
                type_info = extract_type_info(text)

                # text = remove_access_specifiers_and_return_type(text)

                # Check if it is a function or a variable
                is_function = '(' in text and ')' in text
                if is_function:
                    # For functions, add the return type in the function description
                    function_signature = extract_function_signature(text)
                    function_signature = remove_access_specifiers_and_return_type(function_signature)
                    extracted_info["member_functions"].append(f"{access_specifier} {function_signature} : {type_info}")
                else:
                    # Include type information for variables
                    variable_signature = extract_function_signature(text)
                    extracted_info["member_variables"].append(f"{access_specifier} {name} : {type_info}")

    return extracted_info


def remove_access_specifiers_and_return_type(text):
    """
    public, protected, private 등의 접근 지정자 및 함수의 반환형을 텍스트에서 제거합니다.
    """
    # 접근 지정자 제거
    text = re.sub(r'\b(public|protected|private|static|override|virtual|abstract)\b', '', text).strip()
    
    # 함수 반환형을 제거
    # 이 패턴은 함수 시그니처의 시작 부분에 오는 모든 단어를 제거합니다.
    text = re.sub(r'^\b(?:\w+|void)\b\s+', '', text).strip()
    
    return text

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
    # Define the order of access specifiers
    access_order = {'+': 1, '#': 2, '-': 3}

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

def ExtractWitType():
    # Example usage
    all_extracted_info = parse_all_xml_in_folder(xml_folder_path)

    for file_info in all_extracted_info:
        xml_file_name = file_info['file_name']
        result_file_name = format_file_name(xml_file_name)  # Format the file name

        # Create the path for the .txt file in the results folder
        txt_file_path = os.path.join(results_folder_path, result_file_name)

        content = ""
        content += f"Class Name: {file_info['extracted_info']['class_name']}\n"

        member_functions, member_variables = get_sorted_member_info(file_info['extracted_info'])

        content += "Member functions:\n"
        for func in member_functions:
            content += func + "\n"
        content += "Member variables:\n"
        for var in member_variables:
            content += var + "\n"

        print(content)
        create_text_file(txt_file_path, content)  # Use the formatted file path

if __name__ == '__main__':
    ExtractWitType()
