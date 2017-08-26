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
        private int _count = 0;
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
        public int Count { get { return _count; } }
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
                sampler.Vocabulary.Clear();
            }
            log.Info("Cleared the dataset.");
        }

        public void ExportData()
        {
            string[] files = Directory.GetFiles(_sourceDir);
            for (int i = 0; i < files.Length; i++)
            {
                log.InfoFormat("========== Processing file {0} of {1} - {2} =============",
                    i + 1, files.Length,
                    Path.GetFileName(files[i]));

                List<KeyValuePair<string, string>> data = new List<KeyValuePair<string, string>>();
                int fileCounter = 0;
                int dataCount = 0;
                string targetPath = GetTargetFilePath(files[i], fileCounter);

                StreamWriter writer = new StreamWriter(targetPath);
                Action<string> exportDelegate = (dataLine) => {
                    writer.WriteLine(dataLine);
                    if (++dataCount % _maxDataCountPerFile == 0)
                    {
                        writer.Close();
                        writer.Dispose();
                        targetPath = GetTargetFilePath(files[i], ++fileCounter);
                        writer = new StreamWriter(targetPath);
                    };
                };

                //write the data here
                foreach (var sampler in _samplers)
                {
                    sampler.Sample(files[i], exportDelegate);
                    _vocabulary.Merge(sampler.Vocabulary);
                    log.InfoFormat("Updated global vocabulary to {0} words", _vocabulary.Count);
                }
                if(writer != null)
                {
                    writer.Close();
                    writer.Dispose();
                }

                _count += dataCount;
                log.InfoFormat("Saved {0} examples across {1} partitions.", dataCount, fileCounter+1);
            }
            ExportVocabulary();
            log.InfoFormat("Finished exporting the dataset - {0} examples in total.", Count);
        }

        public string GetTargetFilePath(string sourceFilePath, int partitionIndex)
        {
            string targetFileName = Path.GetFileNameWithoutExtension(sourceFilePath) + "_"+partitionIndex.ToString();
            targetFileName += GlobalVariables.DataFileExtension;
            return Path.Combine(_targetDir, targetFileName);
        }
        #endregion
    }
}
