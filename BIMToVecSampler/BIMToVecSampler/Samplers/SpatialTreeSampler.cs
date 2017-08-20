using System;
using System.IO;
using System.Linq;
using Xbim.Ifc;
using Xbim.ModelGeometry.Scene;
using Xbim.Common.XbimExtensions;
using Xbim.Ifc2x3.Kernel;
using System.Collections.Generic;

using Xbim.Common.Geometry;

using BIMToVecSampler.Utils;

namespace BIMToVecSampler.Samplers
{
    public class SpatialTreeSampler: Sampler
    {
        #region-static members
        //later replace this part with units based cell size
        private static double _smallestCellSize = 300;
        #endregion

        #region-fields
        private Dictionary<int, XbimRect3D> _bboxBuffer;
        private Dictionary<int, string> _labelDict;
        private XbimRect3D _boundingBox;
        private XbimOctree<int> _tree;
        #endregion

        #region-properties
        public string IfcFilePath
        {
            get { return _ifcFilePath; }
            set { _ifcFilePath = value; }
        }

        public int ScaleOrder
        {
            get
            {
                double ratio = MathUtil.Max(_boundingBox.SizeX, 
                    _boundingBox.SizeY, _boundingBox.SizeZ)/_smallestCellSize;
                return (int)Math.Ceiling(Math.Log(ratio)/Math.Log(2));
            }
        }
        #endregion

        #region-constructors
        public SpatialTreeSampler(string ifcPath, string dataPath):base(ifcPath, dataPath)
        {
            _bboxBuffer = new Dictionary<int, XbimRect3D>();
            _labelDict = new Dictionary<int, string>();

            _boundingBox = XbimRect3D.Empty;
            using (var model = IfcStore.Open(_ifcFilePath))
            {
                var context = new Xbim3DModelContext(model);
                context.CreateContext();
                List<IfcProduct> prods = model.Instances.OfType<IfcProduct>().ToList();
                foreach (var prod in prods)
                {
                    List<XbimShapeInstance> prodShapes = context.ShapeInstancesOf(prod).Where(p => p.RepresentationType
                    != XbimGeometryRepresentationType.OpeningsAndAdditionsExcluded).Distinct().ToList();

                    if (prodShapes == null || prodShapes.Count == 0) { continue; }
                    XbimRect3D bbox = XbimRect3D.Empty;
                    foreach (var shape in prodShapes)
                    {
                        if (bbox.IsEmpty) { bbox = shape.BoundingBox; }
                        else { bbox.Union(shape.BoundingBox); }
                    }

                    _bboxBuffer.Add(prod.EntityLabel, bbox);
                    _labelDict.Add(prod.EntityLabel, prod.GetType().Name);

                    if (_boundingBox.IsEmpty) { _boundingBox = bbox; }
                    else { _boundingBox.Union(bbox); }
                }
            }

            log.InfoFormat("{0} Objects loaded from the file.", _bboxBuffer.Count);
            ProcessTree();
        }
        #endregion

        #region-methods
        private void ProcessTree()
        {
            double maxSize = MathUtil.Max(_boundingBox.SizeX,
                    _boundingBox.SizeY, _boundingBox.SizeZ);
            double _looseNess = 1.2;
            _tree = new XbimOctree<int>(maxSize/_looseNess, ScaleOrder, _looseNess, _boundingBox.Centroid());

            foreach(int label in _bboxBuffer.Keys) { _tree.Add(label, _bboxBuffer[label]); }

            XbimRect3D treeBox = _tree.ContentBounds();

            string message = MathUtil.BBoxEqual(treeBox, _boundingBox) ? "Tree was successfully populated":
                "Tree bounds do not match the boundingbox of the model !";
            log.Info(message);
        }

        public override void BuildCollections()
        {
            Collections.Clear();
            BuildCollectionsFromTree();
        }

        private void BuildCollectionsFromTree(XbimOctree<int> tree = null)
        {
            tree = tree ?? _tree;
            List<string> collection = GetClassNamesFromEntityLabels(tree.Content().ToList());

            if (collection.Count == 1 && tree.Parent != null)
            {
                collection = GetClassNamesFromEntityLabels(tree.Parent.Content().ToList());
            }

            if (collection.Count > 1) { Collections.Add(collection); }

            foreach (XbimOctree<int> subTree in tree.Subtrees)
            {
                BuildCollectionsFromTree(subTree);
            }
        }

        private List<string> GetClassNamesFromEntityLabels(List<int> labels)
        {
            List<string> classNames = new List<string>();
            foreach (int label in labels)
            {
                classNames.Add(_labelDict[label]);
            }
            return classNames;
        }
        #endregion
    }
}
