using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Xbim.Ifc2x3.ProductExtension;
using Xbim.Ifc2x3.Kernel;
using Xbim.Ifc;

using BIMToVecSampler.Utils;

namespace BIMToVecSampler.Samplers
{
    public class SemanticTreeSampler : Sampler
    {
        #region-fields
        //private IfcProject _project;
        #endregion

        #region-constructors
        public SemanticTreeSampler(string ifcPath):base(ifcPath) { }
        #endregion

        #region-methods
        public void UnpackChildren(IfcObject objIfc)
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
                        UnpackSpatialStructure((IfcSpatialStructureElement)obj);
                    }
                    else
                    {
                        //do nothing ? actually, later try to figure out what these objs are
                    }
                }
            }

            Collections.Add(collection);
        }
        public void UnpackSpatialStructure(IfcSpatialStructureElement structIfc)
        {
            UnpackChildren(structIfc);
            if(structIfc.ContainsElements == null) { return; }

            List<string> collection = new List<string> { structIfc.GetType().Name };
            foreach(IfcRelContainedInSpatialStructure rel in structIfc.ContainsElements)
            {
                foreach(var prod in rel.RelatedElements)
                {
                    collection.Add(prod.GetType().Name);
                }
            }

            Collections.Add(collection);
        }

        public override void BuildCollections()
        {
            using (var model = IfcStore.Open(_ifcFilePath))
            {
                var project = model.Instances.OfType<IfcProject>().FirstOrDefault();
                UnpackChildren(project);
            }
        }
        #endregion
    }
}
