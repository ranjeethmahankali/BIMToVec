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
        List<List<string>> Collections { get; }
        void BuildCollections(IfcStore model);
        void BuildData();
        Vocabulary Vocabulary { get; }
    }

    public abstract class Sampler : ISampler
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        private static List<string> _globalVocabulary = new List<string>();
        private Dataset _dataset;
        private List<KeyValuePair<string, string>> _data;
        protected string _ifcFilePath;

        private static string _datasetPath;

        private List<List<string>> _collections;
        public List<List<string>> Collections
        {
            get
            {
                if(_collections == null) { _collections = new List<List<string>>(); }
                return _collections;
            }
        }
        public List<KeyValuePair<string, string>> Data
        {
            get { return _data; }
        }
        public Dataset Dataset
        {
            get { return _dataset; }
            set { _dataset = value; }
        }
        public Vocabulary Vocabulary
        {
            get
            {
                Vocabulary vocab = new Vocabulary();
                if (_collections == null) { return vocab; }
                foreach(var collection in _collections)
                {
                    vocab.Merge(new Vocabulary(collection));
                }
                return vocab;
            }
        }

        #region-constructors
        public Sampler() { }
        public Sampler(Dataset dataset)
        {
            _dataset = dataset;   
        }
        #endregion

        public abstract void BuildCollections(IfcStore model);
        public void BuildData()
        {
            _data = new List<KeyValuePair<string, string>>();
            foreach (List<string> collection in Collections)
            {
                foreach (string label in collection)
                {
                    foreach (string target in collection)
                    {
                        if (label == target) { continue; }
                        _data.Add(new KeyValuePair<string, string>(label, target));
                    }
                }
            }
        }

        public void Sample(string ifcPath)
        {
            if (!SamplerUtil.IsValidIfcFile(ifcPath))
            {
                throw new FileNotFoundException("The specified IFC file is either invalid or cannot be found.");
            }
            _ifcFilePath = ifcPath;

            try
            {
                using (var model = IfcStore.Open(_ifcFilePath))
                {
                    log.InfoFormat("Loading the file into a {0}...", GetType().Name);
                    Collections.Clear();
                    BuildCollections(model);
                    log.InfoFormat("Finished building {0} collections", Collections.Count);
                }
            }
            catch (Exception e)
            {
                log.ErrorFormat("Failed to load the file: {0}", e.Message);
            }
        }
        public void Clear()
        {
            _collections.Clear();
            _data.Clear();
        }
    }
}
