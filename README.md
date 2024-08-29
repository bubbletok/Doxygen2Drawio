# Doxygen2Drawio

Python program that convert **Doxygen .xml** file into **Drawio .xml** file

It creates a class diagram for each class script one by one

**It does not show any flow, inheritance, or relations of class**

Support with ChatGPT


## Usgae
### Yous should create doxygen .xml files first and follow steps after then.
![image](https://github.com/user-attachments/assets/6b9cca41-f3ba-4e40-aada-6b6c55fabea3)
1. Add .xml files in xmls folder.<br />
   **Not use** the file which ends with "~.xml", but **use the file which ends with "~cs.xml"**<br />
   For example, "test_8cs.xml"
2. Run **doxygen2drawio.py**
3. See drawio folder

You can just drag & drop the .drawio file to the drawio

## Results
- **.txt** files are in **texts** folder <br />
- **.drawio** files are in **drawio** folder <br />
![image](https://github.com/user-attachments/assets/6b3e7a2f-0155-4c88-8146-0a40b394f701)


## Dependency
For install dependencies,
```
pip install -r requirements.txt
```
