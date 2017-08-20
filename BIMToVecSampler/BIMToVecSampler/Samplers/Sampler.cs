using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using Xbim.Common.Logging;
using Xbim.Ifc;
using Xbim.ModelGeometry.Scene;

namespace BIMToVecSampler.Samplers
{
    internal interface ISampler
    {
        List<List<string>> Collections { get; }
        void BuildCollections(IfcStore model);
        List<KeyValuePair<string, string>> Dataset { get; }
        List<string> Vocabulary { get; }
        void UpdateGlobalVocabulary();
    }

    public abstract class Sampler : ISampler
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        protected static readonly string VOCAB_SAVE_FILENAME = "vocabulary.dat";
        private static List<string> _globalVocabulary = new List<string>();
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

        public List<KeyValuePair<string, string>> Dataset
        {
            get
            {
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
                if (_collections == null || _collections.Count == 0) { return new List<string>(); }
                var vocab = new List<string>();
                foreach(var collection in _collections)
                {
                    vocab.AddRange(collection);
                }

                var distinct = vocab.Distinct().ToList();
                return distinct;
            }
        }
        public static List<string> GlobalVocabulary
        {
            get { return _globalVocabulary; }
        }
        public static string DatasetPath
        {
            get
            {
                if(_datasetPath == null) { throw new NullReferenceException("The path of the dataset was not set"); }
                return _datasetPath;
            }
            set
            {
                //now making sure the path provided for data exists and is a valid directory
                FileAttributes attr = File.GetAttributes(value);
                if ((!attr.HasFlag(FileAttributes.Directory)) || (!Directory.Exists(value)))
                {
                    throw new DirectoryNotFoundException("The dataset path provided has to be valid directory !");
                }
                _datasetPath = value;
            }
        }

        #region-constructors
        public Sampler(string ifcPath)
        {
            if (!File.Exists(ifcPath))//making sure the IFC file exists
            {
                throw new FileNotFoundException("The specified IFC file could not be found");
            }
            if(Path.ChangeExtension(Path.GetFileName(ifcPath),".dat") == VOCAB_SAVE_FILENAME)
            {
                throw new FileLoadException(string.Format("Ifc files cannot be named {0} !", Path.GetFileName(ifcPath)));
            }
            _ifcFilePath = ifcPath;

            try
            {
                using (var model = IfcStore.Open(_ifcFilePath))
                {
                    log.InfoFormat("Loading the file into a {0}...", GetType().Name);
                    BuildCollections(model);
                    log.InfoFormat("Finished building {0} collections", Collections.Count);
                    UpdateGlobalVocabulary();
                    log.InfoFormat("Updated global vocabulary to {0} words", _globalVocabulary.Count);
                }
            }
            catch(Exception e)
            {
                log.ErrorFormat("Failed to load the file: {0}", e.Message);
            }
        }
        #endregion

        public abstract void BuildCollections(IfcStore model);
        public void UpdateGlobalVocabulary()
        {
            _globalVocabulary.AddRange(Vocabulary);
            _globalVocabulary = _globalVocabulary.Distinct().ToList();
        }
        public void ExportDataset(bool append = true)
        {
            List<KeyValuePair<string, string>> dataset = Dataset;
            string fileName = Path.ChangeExtension(Path.GetFileName(_ifcFilePath), ".dat");
            using (StreamWriter writer = new StreamWriter(Path.Combine(DatasetPath, fileName), append))
            {
                foreach (KeyValuePair<string, string> pair in dataset)
                {
                    writer.WriteLine(string.Format("{0} {1}", pair.Key, pair.Value));
                }
            }

            log.InfoFormat("{0} the dataset to {1}", append ? "Appended" : "Saved", fileName);
        }

        public static void ExportGlobalVocabulary()
        {
            List<string> vocab = GlobalVocabulary;
            using(StreamWriter writer = new StreamWriter(Path.Combine(DatasetPath, VOCAB_SAVE_FILENAME), false))
            {
                foreach(string word in vocab)
                {
                    writer.WriteLine(word);
                }
            }

            log.InfoFormat("Saved the global vocabulary to {0}", VOCAB_SAVE_FILENAME);
        }
        public static void ClearDataset()
        {
            DirectoryInfo di = new DirectoryInfo(DatasetPath);
            foreach (FileInfo file in di.GetFiles())
            {
                file.Delete();
            }
            foreach (DirectoryInfo dir in di.GetDirectories())
            {
                dir.Delete(true);
            }
        }
    }
}
