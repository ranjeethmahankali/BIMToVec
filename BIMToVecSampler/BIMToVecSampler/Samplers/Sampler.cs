using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using Xbim.ModelGeometry.Scene;

namespace BIMToVecSampler.Samplers
{
    internal interface ISampler
    {
        List<List<string>> Collections { get; }
        void BuildCollections();
        List<KeyValuePair<string, string>> Dataset { get; }
    }

    public abstract class Sampler : ISampler
    {
        protected string _ifcFilePath;
        private List<List<string>> _collections;
        public List<List<string>> Collections
        {
            get
            {
                if(_collections == null) { _collections = new List<List<string>>(); }
                return _collections;
            }
        }

        public List<KeyValuePair<string, string>> Dataset
        {
            get
            {
                BuildCollections();
                List<KeyValuePair<string, string>> dSet = new List<KeyValuePair<string, string>>();
                foreach (List<string> collection in Collections)
                {
                    foreach(string label in collection)
                    {
                        foreach(string target in collection)
                        {
                            if(label == target) { continue; }
                            dSet.Add(new KeyValuePair<string, string>(label, target));
                        }
                    }
                }

                return dSet;
            }
        }

        public Sampler(string ifcPath)
        {
            _ifcFilePath = ifcPath;
        }

        public abstract void BuildCollections();

        public void SaveDatasetAsText(string filePath, bool append = false)
        {
            List<KeyValuePair<string, string>> dataset = Dataset;
            using(StreamWriter writer = new StreamWriter(filePath, append))
            {
                foreach (KeyValuePair<string, string> pair in dataset)
                {
                    writer.WriteLine(string.Format("{0} {1}", pair.Key, pair.Value));
                }
            }
        }
    }
}
