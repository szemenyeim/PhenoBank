from .models import Individual, Property_base, Property, Species, Subspecies, Option
import xlwt
import xml.etree.cElementTree as ET

def constructFileXLS(path, animal):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
    book = xlwt.Workbook()
    ws = book.add_sheet(animal.ENAR)

    ws.write(0, 0, "ENAR:", style0)
    ws.write(0, 1, animal.ENAR)
    ws.write(1, 0, "Name:", style0)
    ws.write(1, 1, animal.Name)
    ws.write(2, 0, "Species:", style0)
    ws.write(2, 1, animal.species.__str__())
    ws.write(3, 0, "Sub Species:", style0)
    ws.write(3, 1, animal.subspecies.__str__())
    ws.write(4, 0, "Sex:", style0)
    ws.write(4, 1, animal.sex)
    ws.write(5, 0, "Location:", style0)
    ws.write(5, 1, animal.location)
    ws.write(6, 0, "Birth Date:", style0)
    ws.write(6, 1, animal.date, style1)

    ws.write(7, 0, "Properties:", style0)

    rowCnt = 8

    properties = Property.objects.filter(animal=animal)
    for property in properties:
        parent = property.parent
        name = parent.name
        type = parent.type
        if (type != 'N'):
            ws.write(rowCnt, 0, name, style0)
            if (type == 'T' or type == 'C'):
                ws.write(rowCnt, 1, property.textVal)
            elif (type == 'F'):
                ws.write(rowCnt, 1, property.numVal)
            rowCnt = rowCnt + 1

    book.save(path)

def WriteChildren(parent,root,animal):
    for node in root.get_children():
        curr = ET.SubElement(parent, node.__str__())
        if node.type == 'N':
            WriteChildren(curr,node,animal)
        else:
            prop = Property.objects.filter(parent=node,animal=animal).first()
            if not prop:
                return
            if node.type == 'F':
                curr.text = str(prop.numVal)
            else:
                curr.text = prop.textVal

def constructFileXML(path, animal):
    root = ET.Element("root")
    phen = ET.SubElement(root, "Phenotype")

    ET.SubElement(phen, "Name").text = animal.Name
    ET.SubElement(phen, "ENAR").text = animal.ENAR
    ET.SubElement(phen, "Species").text = animal.species.__str__()
    ET.SubElement(phen, "Sub Species").text = animal.subspecies.__str__()
    ET.SubElement(phen, "Sex").text = animal.sex
    ET.SubElement(phen, "Location").text = animal.location
    ET.SubElement(phen, "Birth Date").text = animal.date.__str__()

    prop_root = Property_base.objects.filter(species=animal.species).first().get_root()

    prop = ET.SubElement(phen, prop_root.__str__())
    WriteChildren(prop,prop_root,animal)

    tree = ET.ElementTree(root)
    tree.write(path)

def constructFile(path, animal):
    if 'xls' in path:
        constructFileXLS(path,animal)
    elif 'xml' in path:
        constructFileXML(path,animal)
    else:
        return