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
        private Dictionary<int, string> _labelBuffer;
        private XbimRect3D _boundingBox;
        private XbimOctree<int> _tree;
        #endregion

        #region-properties
        public int ScaleOrder
        {
            get
            {
                double ratio = SamplerUtil.Max(_boundingBox.SizeX, 
                    _boundingBox.SizeY, _boundingBox.SizeZ)/_smallestCellSize;
                return (int)Math.Ceiling(Math.Log(ratio)/Math.Log(2));
            }
        }
        #endregion

        #region-constructors
        public SpatialTreeSampler():base() { }
        #endregion

        #region-methods
        private void LoadObjectBuffer(IfcStore model)
        {
            _bboxBuffer = new Dictionary<int, XbimRect3D>();
            _labelBuffer = new Dictionary<int, string>();
            _boundingBox = XbimRect3D.Empty;

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
                _labelBuffer.Add(prod.EntityLabel, prod.GetType().Name);

                if (_boundingBox.IsEmpty) { _boundingBox = bbox; }
                else { _boundingBox.Union(bbox); }
            }

            log.InfoFormat("{0} Objects loaded from the file.", _bboxBuffer.Count);
        }

        private void ProcessTree()
        {
            double maxSize = SamplerUtil.Max(_boundingBox.SizeX, _boundingBox.SizeY, _boundingBox.SizeZ);
            double _looseNess = 1.2;
            _tree = new XbimOctree<int>(maxSize/_looseNess, ScaleOrder, _looseNess, _boundingBox.Centroid());

            foreach(int label in _bboxBuffer.Keys) { _tree.Add(label, _bboxBuffer[label]); }

            XbimRect3D treeBox = _tree.ContentBounds();

            if(SamplerUtil.BBoxEqual(treeBox, _boundingBox)) { log.Info("Tree was successfully populated"); }
            else { log.Error("Tree bounds do not match the boundingbox of the model !"); }
        }

        public override void SampleCollections(IfcStore model, Action<List<string>> collectionSampler)
        {
            LoadObjectBuffer(model);
            ProcessTree();
            SampleCollectionsFromTree(collectionSampler);
        }

        private void SampleCollectionsFromTree(Action<List<string>> collectionSampler, XbimOctree<int> tree = null)
        {
            tree = tree ?? _tree;
            List<string> collection = BuildCollectionFromEntityLabels(tree.Content().ToList());

            if (collection.Count == 1 && tree.Parent != null)
            {
                collection = BuildCollectionFromEntityLabels(tree.Parent.Content().ToList());
            }

            if (collection.Count > 1) { collectionSampler.Invoke(collection); }

            foreach (XbimOctree<int> subTree in tree.Subtrees)
            {
                SampleCollectionsFromTree(collectionSampler, subTree);
            }
        }

        private List<string> BuildCollectionFromEntityLabels(List<int> labels)
        {
            List<string> collection = new List<string>();
            foreach (int label in labels)
            {
                collection.Add(_labelBuffer[label]);
            }
            return collection;
        }
        #endregion
    }
}
