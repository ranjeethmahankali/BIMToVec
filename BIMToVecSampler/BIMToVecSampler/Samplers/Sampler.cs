using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using Xbim.Common.Logging;
using Xbim.ModelGeometry.Scene;

namespace BIMToVecSampler.Samplers
{
    internal interface ISampler
    {
        List<List<string>> Collections { get; }
        void BuildCollections();
        List<KeyValuePair<string, string>> Dataset { get; }
        List<string> Vocabulary { get; }
        void ExportDatasetAsText(bool cleanPrevious = false);
    }

    public abstract class Sampler : ISampler
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        protected static readonly string VOCAB_SAVE_FILENAME = "vocabulary.dat";
        protected string _ifcFilePath, _dataPath;
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
        public List<string> Vocabulary
        {
            get
            {
                var vocab = new List<string>();
                foreach(var collection in _collections)
                {
                    vocab.AddRange(collection);
                }

                return vocab.Distinct().ToList();
            }
        }

        #region-constructors
        public Sampler(string ifcPath, string dataSetPath)
        {
            if (!File.Exists(ifcPath))//making sure the IFC file exists
            {
                throw new FileNotFoundException("The specified IFC file could not be found");
            }
            //now making sure the path provided for data exists and is a valid directory
            FileAttributes attr = File.GetAttributes(dataSetPath);
            if ((!attr.HasFlag(FileAttributes.Directory)) || (!Directory.Exists(dataSetPath)))
            {
                throw new DirectoryNotFoundException("The dataset path provided has to be valid directory !");
            }
            
            _ifcFilePath = ifcPath;
            _dataPath = dataSetPath;
        }
        #endregion

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

        public void SaveVocabularyAsText(string filePath, bool append = true)
        {
            if(_collections == null || _collections.Count == 0) { return; }
            List<string> vocab = Vocabulary;
            using(StreamWriter writer = new StreamWriter(filePath))
            {
                foreach(string word in vocab)
                {
                    writer.WriteLine(word);
                }
            }
        }

        public void ExportDatasetAsText(bool cleanPrev = false)
        {
            //if this bool is true, then we have to clean up the dataset that is existing before exporting
            if (cleanPrev)
            {
                DirectoryInfo di = new DirectoryInfo(_dataPath);
                foreach(FileInfo file in di.GetFiles())
                {
                    file.Delete();
                }
                foreach (DirectoryInfo dir in di.GetDirectories())
                {
                    dir.Delete(true);
                }
            }

            string fileName = Path.ChangeExtension(Path.GetFileName(_ifcFilePath), ".dat");
            SaveDatasetAsText(Path.Combine(_dataPath, fileName));
            SaveVocabularyAsText(Path.Combine(_dataPath, VOCAB_SAVE_FILENAME));
        }
    }
}
