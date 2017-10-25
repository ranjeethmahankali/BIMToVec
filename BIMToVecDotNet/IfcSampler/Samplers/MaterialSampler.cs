using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xbim.Ifc;
using Xbim.Ifc2x3.Kernel;
using Xbim.Ifc2x3.ProductExtension;
using Xbim.Ifc2x3.MaterialResource;

namespace IfcSampler.Samplers
{
    public class MaterialSampler : Sampler
    {
        #region-constructors
        public MaterialSampler() { }
        #endregion

        #region-methods
        public override void SampleCollections(IfcStore model, Action<List<string>> collectionSampler)
        {
            var relMats = model.Instances.OfType<IfcRelAssociatesMaterial>();
            foreach(var relMat in relMats)
            {
                List<string> collection = SampleRelMaterial(relMat);
                collectionSampler.Invoke(collection);
            }
        }

        private List<string> SampleRelMaterial(IfcRelAssociatesMaterial relMat)
        {
            var collection = new List<string>();
            foreach(var obj in relMat.RelatedObjects)
            {
                collection.Add(obj.GetType().Name);
            }

            if (typeof(IfcMaterial).IsAssignableFrom(relMat.RelatingMaterial.GetType()))
            {
                var mat = (IfcMaterial)relMat.RelatingMaterial;
                collection.Add(mat.Name);
            }
            else if (typeof(IfcMaterialList).IsAssignableFrom(relMat.RelatingMaterial.GetType()))
            {
                var matList = (IfcMaterialList)relMat.RelatingMaterial;
                foreach(var mat in matList.Materials)
                {
                    collection.Add(mat.Name);
                }
            }
            else if (typeof(IfcMaterialLayerSet).IsAssignableFrom(relMat.RelatingMaterial.GetType()))
            {
                var matLayerSet = (IfcMaterialLayerSet)relMat.RelatingMaterial;
                collection.Add(matLayerSet.LayerSetName);
                foreach(var matLayer in matLayerSet.MaterialLayers)
                {
                    collection.Add(matLayer.Material.Name);
                }
            }
            else if (typeof(IfcMaterialLayer).IsAssignableFrom(relMat.RelatingMaterial.GetType()))
            {
                var matLayer = (IfcMaterialLayer)relMat.RelatingMaterial;
                collection.Add(matLayer.Material.Name);

            }
            else if (typeof(IfcMaterialLayerSetUsage).IsAssignableFrom(relMat.RelatingMaterial.GetType()))
            {
                var mLSetUsage = (IfcMaterialLayerSetUsage)relMat.RelatingMaterial;
                collection.Add(mLSetUsage.ForLayerSet.LayerSetName);
                foreach(var matLayer in mLSetUsage.ForLayerSet.MaterialLayers)
                {
                    collection.Add(matLayer.Material.Name);
                }
            }

            return collection;
        }
        #endregion
    }
}
