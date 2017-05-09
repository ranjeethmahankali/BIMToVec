"""
The dimensions for the geometry mentioned in this script are interpreted as feet
even though the project units in the document are millimeters. This could be because my revit
installation is imperial system, i.e. all the default templates have imperial units. That could
be the reason for feet.
"""
#import libraries and reference the RevitAPI and RevitAPIUI
import clr
import math
import random
 
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

#main code starts
#make sure 3d view is active and the section box is turned on
#or else it won't know where to look
bigbox = doc.ActiveView.GetSectionBox()
minPt = bigbox.Min
maxPt = bigbox.Max

size = 2
path = 'output.txt'
f = open(path, 'w')
f.truncate()
for i in range(10000):
	pt1 = XYZ(random.uniform(minPt.X,maxPt.X),
				random.uniform(minPt.Y,maxPt.Y),
				random.uniform(minPt.Z,maxPt.Z))
	diagonal = XYZ(size,size,size)
	pt2 = pt1.Add(diagonal)
	box = Outline(pt1, pt2)
	
	filter = BoundingBoxIntersectsFilter(box)
	notCamFilter = ElementCategoryFilter(BuiltInCategory.OST_Cameras, True)
	notSketchFilter = ElementClassFilter(Sketch, True)
	notTopoFilter = ElementCategoryFilter(BuiltInCategory.OST_Topography,True)
	notLines = ElementClassFilter(CurveElement, True)
	
	collector = FilteredElementCollector(doc)
	
	collector = collector.WherePasses(filter).WherePasses(notCamFilter).WherePasses(notSketchFilter)
	collector = collector.WherePasses(notTopoFilter).WherePasses(notLines)
	collector = collector.WhereElementIsNotElementType().WhereElementIsViewIndependent()
	elemList = collector.ToElements()
	
	if elemList.Count < 2:continue
	#print(elemList.Count)
	for i in range(elemList.Count):
		if elemList[i].Category.Name == "<Sketch>":
			print(elemList[i])
		#if not elemList[i].Category is None
		matList = elemList[i].GetMaterialIds(False)
		matNames = []
		for mat in matList:
			matNames.append(doc.GetElement(mat).MaterialCategory)
		f.write(elemList[i].Category.Name+"; M: "+",".join(matNames)+"\n")
		#f.write(type(elemList[i]).__name__+"; M: "+",".join(matNames)+"\n")
		#print(elemList[i].Category.Name+"; M: "+",".join(matNames)+"\n")
	f.write('-------------\n')
f.close()

"""
pt1 = XYZ(0,0,0)
pt2 = XYZ(0,size,0)
pt3 = XYZ(size,size,0)
pt4 = XYZ(size,0,0)

l1 = Line.CreateBound(pt1, pt2)
l2 = Line.CreateBound(pt2, pt3)
l3 = Line.CreateBound(pt3, pt4)
l4 = Line.CreateBound(pt4, pt1)

loop = CurveLoop.Create([l1,l2,l3,l4])

box = GeometryCreationUtilities.CreateExtrusionGeometry([loop], XYZ(0,0,1), 25)

t = Transaction(doc, "adding stuff")
t.Start()
ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
ds.ApplicationId = "app id"
ds.ApplicationDataId = "obj id"
ds.SetShape([box])
t.Commit()
"""