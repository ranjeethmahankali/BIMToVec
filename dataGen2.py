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
import sys
 
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

testFam = None

#main code starts
#make sure 3d view is active and the section box is turned on
#or else it won't know where to look
bigbox = doc.ActiveView.GetSectionBox()
minPt = bigbox.Min
maxPt = bigbox.Max

matsToSkip = ["Miscellaneous","Unassigned", "Generic"]

size = 2
path = 'output.txt'
f = open(path, 'w')
f.truncate()
for _ in range(100):
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
			materialCategory = doc.GetElement(mat).MaterialCategory
			if materialCategory in matsToSkip:continue
			matNames.append(materialCategory)
		f.write(elemList[i].Category.Name+"; M: "+",".join(matNames)+"\n")
		if type(elemList[i]).__name__ == "FamilyInstance":
			#processFamily(elemList[i])
			print(elemList[i].Id.IntegerValue, elemList[i].Name)
	f.write('-------------\n')
	#sys.stdout.write("Sample# %s\r"%i)
f.close()