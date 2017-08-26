using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using Xbim.Common.Logging;
using BIMToVecSampler.Samplers;
using BIMToVecSampler.Utils;

namespace BIMToVecSampler
{
    public class Dataset
    {
        #region-fields
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        private string _sourceDir, _targetDir;
        private List<Sampler> _samplers = new List<Sampler>();
        private int _maxDataCountPerFile = 35000;
        private Vocabulary _vocabulary = new Vocabulary();
        #endregion

        #region-properties
        public string TargetDir
        {
            get { return _targetDir; }
        }

        public Vocabulary Vocabulary
        {
            get { return _vocabulary; }
        }
        public int MaxDataCountPerFile
        {
            get { return _maxDataCountPerFile; }
            set { _maxDataCountPerFile = value; }
        }
        #endregion

        #region-constructors
        public Dataset(string source, string target, List<Sampler> samplers)
        {
            _sourceDir = SamplerUtil.GetAbsoluteFilePath(source);
            _targetDir = SamplerUtil.GetAbsoluteFilePath(target);

            foreach(var sampler in samplers)
            {
                AddSampler(sampler);
            }
        }
        public Dataset(string source, string target) : this(source, target, new List<Sampler>()) { }
        #endregion

        #region-methods
        public void AddSampler(Sampler sampler)
        {
            _samplers.Add(sampler);
            sampler.Dataset = this;
        }
        public void ExportVocabulary()
        {
            using (StreamWriter writer = new StreamWriter(Path.Combine(_targetDir, GlobalVariables.VOCAB_SAVE_FILENAME), false))
            {
                foreach (string word in _vocabulary)
                {
                    writer.WriteLine(word);
                }
            }

            log.InfoFormat("Saved the global vocabulary to {0}", GlobalVariables.VOCAB_SAVE_FILENAME);
        }

        public void Clear()
        {
            //log.Info("Clearing the dataset.");
            DirectoryInfo di = new DirectoryInfo(_targetDir);
            foreach (FileInfo file in di.GetFiles())
            {
                file.Delete();
            }
            foreach (DirectoryInfo dir in di.GetDirectories())
            {
                dir.Delete(true);
            }

            Vocabulary.Clear();

            foreach(var sampler in _samplers)
            {
                sampler.Collections.Clear();
            }
            log.Info("Cleared the dataset.");
        }

        public void ExportData()
        {
            string[] files = Directory.GetFiles(_sourceDir);
            for (int i = 0; i < files.Length; i++)
            {
                log.InfoFormat("========== Processing the file {0} =============", Path.GetFileName(files[i]));
                List<KeyValuePair<string, string>> data = new List<KeyValuePair<string, string>>();
                foreach (var sampler in _samplers)
                {
                    sampler.Sample(files[i]);
                    sampler.BuildData();
                    data.AddRange(sampler.Data);
                    _vocabulary.Merge(sampler.Vocabulary);
                    log.InfoFormat("Updated global vocabulary to {0} words", _vocabulary.Count);
                    sampler.Clear();//to save memory
                }

                PartitionDataAndExport(data, _maxDataCountPerFile, files[i]);
            }
            ExportVocabulary();
        }

        public void PartitionDataAndExport(List<KeyValuePair<string, string>> _data, int maxCountPerFile,
            string filePath)
        {
            List<List<KeyValuePair<string, string>>> dataPartitions = SamplerUtil.PartitionList(_data, maxCountPerFile);

            int numPartitions = dataPartitions.Count;
            bool split = numPartitions > 1;
            int i = 0;
            foreach (var partition in dataPartitions)
            {
                string targetFileName = Path.GetFileNameWithoutExtension(filePath);
                targetFileName += string.Format("{0}{1}", split ? "_" + i.ToString() : "", GlobalVariables.DataFileExtension);
                string targetPath = Path.Combine(_targetDir, targetFileName);
                using (StreamWriter writer = new StreamWriter(targetPath))
                {
                    foreach (KeyValuePair<string, string> pair in partition)
                    {
                        writer.WriteLine(string.Format("{0} {1}", pair.Key, pair.Value));
                    }
                }

                log.InfoFormat("Saved partition {0} of {1}", i + 1, numPartitions);
                i++;
            }

            log.InfoFormat("Finished saving the data.");
        }
        #endregion
    }
}
