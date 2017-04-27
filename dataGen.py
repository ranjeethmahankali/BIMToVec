"""
The dimensions for the geometry mentioned in this script are interpreted as feet
even though the project units in the document are millimeters. This could be because my revit
installation is imperial system, i.e. all the default templates have imperial units. That could
be the reason for feet.
"""
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
		matList = elemList[i].GetMaterialIds(False)
		matNames = []
		for mat in matList:
			matNames.append(doc.GetElement(mat).Name)
		print(elemList[i].Category.Name, matNames)



"""
pt1 = XYZ(0,0,0)
pt2 = XYZ(0,20,0)
pt3 = XYZ(20,20,0)
pt4 = XYZ(20,0,0)

l1 = Line.CreateBound(pt1, pt2)
l2 = Line.CreateBound(pt2, pt3)
l3 = Line.CreateBound(pt3, pt4)
l4 = Line.CreateBound(pt4, pt1)

loop = CurveLoop.Create([l1,l2,l3,l4])

box = GeometryCreationUtilities.CreateExtrusionGeometry([loop], XYZ(0,0,1), 20)

t = Transaction(doc, "adding stuff")
t.Start()
ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
ds.ApplicationId = "app id"
ds.ApplicationDataId = "obj id"
ds.SetShape([box])
t.Commit()
"""