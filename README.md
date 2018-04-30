# BIMToVec
BIMToVec is an embeddings set for the vocabulary used in BIM models, which includes building object names and material names. The training technique is similar in principle to how word embeddings are trained in NLP, but is adapted to sample the vocabulary from BIM models instead of a corpus of text.

BIMToVec/IfcSampler/ is a C# project that uses XBim toolkit (installed as a NuGet package) to sample IFC files for related labels (vocabulary). It uses 3 types of sampling logics (1) Spatial Sampling: sampling labels associated with building objects that are in spatial proximity of each other. (2) Material Sampling: sampling object names and names of the materials used by those objects. (3) Containment Tree Sampling: sampling lables associated with building objects that are in proximity of each other in the IFC containment tree.

BIMToVec/RevitBIMToVec/ is a Revit 2017 add-in that can connect to a python server (model_server.py) to query the embeddings for various Revit objects, and then use them to draw inferences about those objects. Though not currently implemented, this could potentially be used for anomaly detection in Revit models, given the quality of embeddings served by the python server is high.

model_embeddings.py defines the model and train_embeddings.py runs the training.
