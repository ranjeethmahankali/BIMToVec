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
import pickle
 
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

# returns an cube shaped outline object
def GetOutlineAt(center, size):
	hdiag = XYZ(size/2, size/2, size/2)
	pt1 = center.Subtract(hdiag)
	pt2 = center.Add(hdiag)

	return Outline(pt1, pt2)
# random coin toss - returns true or false
# can specify the probability of true if you want uneven odds
def coinToss(trueProb = 0.5):
	rand = random.random()
	return rand < trueProb

# takes an Outline object and adds the corresponding box geometry to the document as a generic model
def AddBoxToDoc(box):
	size = box.MaximumPoint.Z -box.MinimumPoint.Z

	pt1 = box.MinimumPoint
	pt2 = pt1.Add(XYZ(0,size,0))
	pt3 = pt1.Add(XYZ(size,size,0))
	pt4 = pt1.Add(XYZ(size,0,0))

	l1 = Line.CreateBound(pt1, pt2)
	l2 = Line.CreateBound(pt2, pt3)
	l3 = Line.CreateBound(pt3, pt4)
	l4 = Line.CreateBound(pt4, pt1)

	loop = CurveLoop.Create([l1,l2,l3,l4])

	box = GeometryCreationUtilities.CreateExtrusionGeometry([loop], XYZ(0,0,1), size)

	t = Transaction(doc, "adding stuff")
	t.Start()
	ds = DirectShape.CreateElement(doc, ElementId(BuiltInCategory.OST_GenericModel))
	ds.ApplicationId = "app id"
	ds.ApplicationDataId = "obj id"
	ds.SetShape([box])
	t.Commit()

# instances of this class will contain the data collected in one window
class elementSet:
	# constructor
	def __init__(self, elementNames, materialDictionary):
		self.elements = elementNames
		# this is a dictionary where the keys are the element names and
		# values are sets containing the material names associated with that element
		self.matDict = materialDictionary
	# generate pairs of vocabulary from the set
	def GeneratePairs(self,num):
		labels = list()
		targets = list()
		# populate these lists now
		i = 0
		while i < num:
			pair = None
			if coinToss() and len(self.elements) > 1:
				pair = random.sample(self.elements, 2)
				i += 1
			else:
				randElem = random.sample(self.elements, 1)[0]
				if len(self.matDict[randElem]) < 1:
					i += 1
					continue
				else:
					matName = random.sample(self.matDict[randElem], 1)[0]
					pair = [randElem, matName] if coinToss() else [matName, randElem]
					i += 1
			
			labels.append(pair[0])
			targets.append(pair[1])

		return [labels, targets]

#This applies all the needed filters and returns an element collector for the document
# the collector will only collec the elements that intersect with the box
def GetCollector(box, doc):
	filter = BoundingBoxIntersectsFilter(box)
	notCamFilter = ElementCategoryFilter(BuiltInCategory.OST_Cameras, True)
	notSketchFilter = ElementClassFilter(Sketch, True)
	notTopoFilter = ElementCategoryFilter(BuiltInCategory.OST_Topography,True)
	notLines = ElementClassFilter(CurveElement, True)

	collector = FilteredElementCollector(doc)
	
	collector = collector.WherePasses(filter).WherePasses(notCamFilter).WherePasses(notSketchFilter)
	collector = collector.WherePasses(notTopoFilter).WherePasses(notLines)
	collector = collector.WhereElementIsNotElementType().WhereElementIsViewIndependent()

	return collector

#this takes a revit element and returns the material category names associated with that element
def GetMaterials(element):
	matsToSkip = ["Miscellaneous","Unassigned", "Generic"]
	matList = element.GetMaterialIds(False)
	matNames = set()
	for mat in matList:
		materialCategory = doc.GetElement(mat).MaterialCategory
		if materialCategory in matsToSkip:continue
		matNames.add(materialCategory)
	
	return matNames

# returns a small box (randomly) of given size from inside the container box
def GetBox(container, size):
	minPt = container.Transform.OfPoint(container.Min)
	maxPt = container.Transform.OfPoint(container.Max)

	randX = random.random()
	randY = random.random()
	randZ = random.random()

	if randX > 0.5 or randY > 0.5 or randZ > 0.5: print(randX, randY, randZ)

	center = XYZ(
		randX*(minPt.X) + (1-randX)*maxPt.X,
		randY*(minPt.Y) + (1-randY)*maxPt.Y,
		randZ*(minPt.Z) + (1-randZ)*maxPt.Z
	)

	# ratio = (center.X - minPt.X)/(maxPt.X - minPt.X)
	# print(ratio)

	# center = XYZ(
	# 	random.uniform(minPt.X + (size/2), maxPt.X - (size/2)),
	# 	random.uniform(minPt.Y + (size/2), maxPt.Y - (size/2)),
	# 	random.uniform(maxPt.Z - 7, maxPt.Z)
	# )

	box = GetOutlineAt(center, size)
	AddBoxToDoc(box) # this is for debugging reasons
	return box
# writes the variable to the given path
def writeToFile(data, path):
	with open(path, 'wb') as writer:
		pickle.dump(data, writer, pickle.HIGHEST_PROTOCOL)

# global variables
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document

#make sure 3d view is active and the section box is turned on
#or else it won't know where to look
bigbox = doc.ActiveView.GetSectionBox()
print(bigbox.Max.Z - bigbox.Min.Z)


WINDOW_SIZE = 2 # this is in feet. trying to use a 2ft cube as a capture window
textPath = '../data/DataAsText.txt' # the text version of dataset will be saved to this file
dataPath = "../data/%02d.pkl" % 0
wordsFile = "../data/wordList.pkl"

def GenerateData(cycleNum):
	labels = []
	targets = []
	f_text = open(textPath, 'w')
	f_text.truncate()
	for _ in range(cycleNum):
		window = GetBox(bigbox, WINDOW_SIZE)
		#AddBoxToDoc(window)
		elemList = GetCollector(window, doc).ToElements()
		elemNameSet = set()
		materialDict = dict()
		if elemList.Count < 1:
			# print("slipping - %s" % elemList.Count)
			continue #too few elements collected
		for i in range(elemList.Count):
			matNames = GetMaterials(elemList[i])
			f_text.write(elemList[i].Category.Name+"; M: "+",".join(matNames)+"\n")
			
			elemNameSet.add(elemList[i].Category.Name)
			materialDict[elemList[i].Category.Name] = matNames
			#print("here")
			elemBatch = elementSet(elemNameSet, materialDict)
			batch = elemBatch.GeneratePairs(2)
			labels += batch[0]
			targets += batch[1]

		f_text.write('-------------\n')
	f_text.close()

	return [labels, targets]


# Generating the data
labels, targets = GenerateData(1000)
allWords = set()
allWords = allWords.union(set(labels))

allWords = allWords.union(set(targets))
# printing the generated pairs for debugging reasons
# for i in range(len(labels)):
# 	print("%03d - %s - %s"%(i, labels[i], targets[i]))

# now pickling the data on the disk to the predefined path
writeToFile([labels, targets], dataPath)
writeToFile(allWords, wordsFile)

print(len(allWords))