#import libraries and reference the RevitAPI and RevitAPIUI
import clr
import math
 
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI') 
from Autodesk.Revit.DB import *

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

#filter = ElementCategoryFilter(BuiltInCategory.OST_Topography)
#collector = FilteredElementCollector(doc)

#elemList = collector.WherePasses(filter).WhereElementIsNotElementType().ToElements()
#print(elemList.Count)

pt1 = XYZ(0,0,0)
pt2 = XYZ(20,20,20)
box = Outline(pt1, pt2)


filter = BoundingBoxIntersectsFilter(box)
collector = FilteredElementCollector(doc)

elemList = collector.WherePasses(filter).WhereElementIsNotElementType().ToElements()
for i in range(elemList.Count):
	if not elemList[i].Category is None:
		print(elemList[i].Category.Name)
		