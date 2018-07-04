from .models import Individual, Property_base, Property, Location, Species, Subspecies, Option
import xlwt

def constructFile(path, animal):
    style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                         num_format_str='#,##0.00')
    style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
    book = xlwt.Workbook()
    ws = book.add_sheet(animal.ENAR)

    ws.write(0,0,"ENAR:",style0)
    ws.write(0,1,animal.ENAR)
    ws.write(1,0,"Name:",style0)
    ws.write(1,1,animal.Name)
    ws.write(2,0,"Species:",style0)
    ws.write(2,1,animal.species.__str__())
    ws.write(3,0,"Sub Species:",style0)
    ws.write(3,1,animal.subspecies.__str__())
    ws.write(4,0,"Gender:",style0)
    ws.write(4,1,animal.gender)
    ws.write(5,0,"Location:",style0)
    ws.write(5,1,animal.location.__str__())
    ws.write(6,0,"Birth Date:",style0)
    ws.write(6,1,animal.date,style1)

    ws.write(7,0,"Properties:",style0)

    rowCnt = 8

    properties = Property.objects.filter(animal=animal)
    for property in properties:
        parent = property.parent
        name = parent.name
        type = parent.type
        if( type != 'N'):
            ws.write(rowCnt,0,name,style0)
            if( type == 'T' or type == 'C' ):
                ws.write(rowCnt,1,property.textVal)
            elif( type == 'F' ):
                ws.write(rowCnt,1,property.numVal)
            rowCnt = rowCnt + 1

    book.save(path)