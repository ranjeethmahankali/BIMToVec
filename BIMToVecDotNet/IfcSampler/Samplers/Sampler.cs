using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using IfcSampler.Utils;

using Xbim.Common.Logging;
using Xbim.Ifc;
using Xbim.ModelGeometry.Scene;

namespace IfcSampler.Samplers
{
    public abstract class Sampler
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();

        #region-constructors
        public Sampler() { }
        #endregion

        public abstract void SampleCollections(IfcStore model, Action<List<string>> collectionSampler);
        public void ExportData(IfcStore model, Action<string,string> exportDelegate, Action<List<string>> vocabMerger)
        {
            int numCollections = 0;
            Action<List<string>> collectionSampler = (collection) => {
                collection = SamplerUtil.ProcessCollection(collection);
                vocabMerger.Invoke(collection);//add the collection to the global vocabulary
                foreach (string label in collection)
                {
                    foreach (string target in collection)
                    {
                        if (label == target) { continue; }
                        exportDelegate.Invoke(label, target);
                    }
                }
                numCollections++;
            };

            SampleCollections(model, collectionSampler);
            log.InfoFormat("Finished sampling {0} collections", numCollections);
        }

        public void Sample(string ifcPath, Action<string,string> exportDelegate, Action<List<string>> vocabUpdaterDelegate)
        {
            if (!SamplerUtil.IsValidIfcFile(ifcPath))
            {
                throw new FileNotFoundException("The specified IFC file is either invalid or cannot be found.");
            }

            try
            {
                using (var model = IfcStore.Open(ifcPath))
                {
                    log.InfoFormat("Sampling the file with a {0}...", GetType().Name);
                    ExportData(model, exportDelegate, vocabUpdaterDelegate);
                }
            }
            catch (Exception e)
            {
                log.ErrorFormat("Failed to load the file: {0}", e.Message);
            }
        }
    }
}
