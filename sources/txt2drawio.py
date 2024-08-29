import xml.etree.ElementTree as ET
import os
import shutil
# XML 구조 정의
def create_class_diagram(file_path, output_folder):
    def indent(elem, level=0):
        """Recursively indent XML elements for pretty printing"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # XML의 루트 요소 생성
    mxfile = ET.Element('mxfile', {
        'host': 'Electron',
        'agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) draw.io/24.7.5 Chrome/126.0.6478.183 Electron/31.3.0 Safari/537.36',
        'version': '24.7.5'
    })

    # 다이어그램 요소 생성
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'C5RBs43oDa-KdzZeNtuy',
        'name': 'Page-1'
    })

    # mxGraphModel 요소 생성
    mxGraphModel = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '516',
        'dy': '494',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': '827',
        'pageHeight': '1169',
        'math': '0',
        'shadow': '0'
    })

    # root 요소 생성
    root = ET.SubElement(mxGraphModel, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    class_name, member_vars, member_funcs = extract_class_info(file_path)

    # Class Box
    class_box = ET.SubElement(root, 'mxCell', {
        'id': '2',
        'value': class_name,
        'style': 'swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(class_box, 'mxGeometry', {
        'x': '480',
        'y': '100',
        'width': '300',
        'height': '500',
        'as': 'geometry'
    })

    # Member Variables
    y_position = 26
    for var in member_vars:
        ET.SubElement(root, 'mxCell', {
            'id': str(len(root)),
            'value': var,
            'style': 'text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;',
            'vertex': '1',
            'parent': '2'
        }).append(
            ET.Element('mxGeometry', {
                'y': str(y_position),
                'width': '300',
                'height': '26',
                'as': 'geometry'
            })
        )
        y_position += 26

    # Separator
    ET.SubElement(root, 'mxCell', {
        'id': str(len(root)),
        'style': 'line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;strokeColor=inherit;',
        'vertex': '1',
        'parent': '2'
    }).append(
        ET.Element('mxGeometry', {
            'y': str(y_position),
            'width': '300',
            'height': '8',
            'as': 'geometry'
        })
    )
    y_position += 8

    # Member Functions
    for func in member_funcs:
        ET.SubElement(root, 'mxCell', {
            'id': str(len(root)),
            'value': func,
            'style': 'text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;',
            'vertex': '1',
            'parent': '2'
        }).append(
            ET.Element('mxGeometry', {
                'y': str(y_position),
                'width': '300',
                'height': '26',
                'as': 'geometry'
            })
        )
        y_position += 26

    # XML 트리 생성 및 저장
    indent(mxfile)  # 적용된 들여쓰기
    
    output_file_name = os.path.basename(file_path).replace('.txt', '_Diagram.drawio')
    output_file_path = os.path.join(output_folder, output_file_name)

    tree = ET.ElementTree(mxfile)
    tree.write(output_file_path, encoding='UTF-8', xml_declaration=True)

def extract_class_info(txt_file):
    with open(txt_file, 'r') as file:
        lines = file.readlines()

    class_name = ""
    member_functions = []
    member_variables = []
    
    parsing_functions = False
    parsing_variables = False

    for line in lines:
        line = line.strip()
        if line.startswith('Class Name:'):
            # Remove '.cs' from the class name if it exists
            class_name = line.split(':', 1)[1].strip().replace('.cs', '')
        elif line.startswith('Member functions:'):
            parsing_functions = True
            parsing_variables = False
        elif line.startswith('Member variables:'):
            parsing_functions = False
            parsing_variables = True
        elif parsing_functions and line:
            # Capture the entire function line
            member_functions.append(f"{line}")
        elif parsing_variables and line:
            # Capture the entire variable line
            member_variables.append(f"{line}")
    
    return class_name, member_functions, member_variables

def process_all_files_in_folder(folder_path, output_folder):
    # Output folder 생성 및 XML 파일 저장
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # 폴더를 비운 후 다시 생성
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            create_class_diagram(file_path, output_folder)

def txtToDrawio():
    folder_path = 'texts'
    output_folder = 'drawio'
    process_all_files_in_folder(folder_path, output_folder)

if __name__ == '__main__':
    txtToDrawio()
