using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Xbim.Ifc2x3.ProductExtension;
using Xbim.Ifc2x3.Kernel;
using Xbim.Ifc;

using IfcSampler.Utils;

namespace IfcSampler.Samplers
{
    public class SemanticTreeSampler : Sampler
    {
        #region-fields
        //private IfcProject _project;
        #endregion

        #region-constructors
        public SemanticTreeSampler():base() { }
        #endregion

        #region-methods
        public void SampleChildren(IfcObject objIfc, Action<List<string>> collectionSampler)
        {
            List<IfcRelDecomposes> decomposed = objIfc.IsDecomposedBy.ToList();
            if(decomposed == null || decomposed.Count == 0) { return; }
            List<string> collection = new List<string> { objIfc.GetType().Name };

            foreach(var dec in decomposed)
            {
                foreach(var obj in dec.RelatedObjects)
                {
                    collection.Add(obj.GetType().Name);
                    if (typeof(IfcSpatialStructureElement).IsAssignableFrom(obj.GetType()))
                    {
                        SampleSpatialStructure((IfcSpatialStructureElement)obj, collectionSampler);
                    }
                    else
                    {
                        //do nothing ? actually, later try to figure out what these objs are
                    }
                }
            }

            collectionSampler.Invoke(collection);
        }
        public void SampleSpatialStructure(IfcSpatialStructureElement structIfc, Action<List<string>> collectionSampler)
        {
            SampleChildren(structIfc, collectionSampler);
            if(structIfc.ContainsElements == null) { return; }

            List<string> collection = new List<string> { structIfc.GetType().Name };
            foreach(IfcRelContainedInSpatialStructure rel in structIfc.ContainsElements)
            {
                foreach(var prod in rel.RelatedElements)
                {
                    collection.Add(prod.GetType().Name);
                }
            }

            collectionSampler.Invoke(collection);
        }

        public override void SampleCollections(IfcStore model, Action<List<string>> collectionSampler)
        {
            var project = model.Instances.OfType<IfcProject>().FirstOrDefault();
            SampleChildren(project, collectionSampler);
        }
        #endregion
    }
}
