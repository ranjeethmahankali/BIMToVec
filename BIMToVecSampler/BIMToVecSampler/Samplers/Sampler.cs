using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using BIMToVecSampler.Utils;

using Xbim.Common.Logging;
using Xbim.Ifc;
using Xbim.ModelGeometry.Scene;

namespace BIMToVecSampler.Samplers
{
    internal interface ISampler
    {
        void SampleCollections(IfcStore model, Action<List<string>> collectionSampler);
        void ExportData(IfcStore model, Action<string> exportDelegate);
        Vocabulary Vocabulary { get; }
    }

    public abstract class Sampler : ISampler
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        private Vocabulary _vocabulary = new Vocabulary();

        public Vocabulary Vocabulary
        {
            get { return _vocabulary; }
        }

        #region-constructors
        public Sampler() { }
        #endregion

        public abstract void SampleCollections(IfcStore model, Action<List<string>> collectionSampler);
        public void ExportData(IfcStore model, Action<string> exportDelegate)
        {
            int numCollections = 0;
            Action<List<string>> collectionSampler = (collection) => {
                foreach (string label in collection)
                {
                    foreach (string target in collection)
                    {
                        if (label == target) { continue; }
                        exportDelegate.Invoke(string.Format("{0} {1}", label, target));
                    }
                }

                _vocabulary.Add(collection);
                numCollections++;
            };

            SampleCollections(model, collectionSampler);
            log.InfoFormat("Finished sampling {0} collections", numCollections);
        }

        public void Sample(string ifcPath, Action<string> exportDelegate)
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
                    ExportData(model, exportDelegate);
                }
            }
            catch (Exception e)
            {
                log.ErrorFormat("Failed to load the file: {0}", e.Message);
            }
        }
    }
}
