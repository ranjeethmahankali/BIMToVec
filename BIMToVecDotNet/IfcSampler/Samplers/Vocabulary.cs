using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using Xbim.Common.Logging;

namespace BIMToVecSampler.Samplers
{
    public class Vocabulary : ICollection<string>
    {
        protected static readonly ILogger log = LoggerFactory.GetLogger();
        private List<string> _vocab = new List<string>();
        public List<string> Words
        {
            get { return _vocab; }
        }
        //private Dictionary<string, int> IndexDictionary

        public Vocabulary() { }
        public Vocabulary(List<string> words)
        {
            _vocab.AddRange(words);
            _vocab = _vocab.Distinct().ToList();
        }

        public int IndexOf(string word)
        {
            int index = _vocab.IndexOf(word);
            if(index == -1)
            {
                throw new ArgumentException("The word cannot be found in the vocabulary !");
            }
            return index;
        }
        public int Count { get { return _vocab.Count; } }
        public bool IsReadOnly { get { return false; } }
        public void Add(string item)
        {
            if (!Contains(item))
            {
                _vocab.Add(item);

            }
        }
        public void Clear() { _vocab.Clear(); }
        public bool Contains(string item) { return _vocab.Contains(item); }
        public void CopyTo(string[] array, int arrayIndex){ _vocab.CopyTo(array, arrayIndex); }
        public IEnumerator<string> GetEnumerator()
        { return _vocab.GetEnumerator(); }
        public bool Remove(string item) { return _vocab.Remove(item); }
        IEnumerator IEnumerable.GetEnumerator() { return this.GetEnumerator(); }

        public void Merge(Vocabulary newVocab)
        {
            _vocab.AddRange(newVocab.Words);
            _vocab = _vocab.Distinct().ToList();
        }
        public void Add(List<string> words)
        {
            _vocab.AddRange(words);
            _vocab = _vocab.Distinct().ToList();
        }

        public void Export(string targetPath)
        {
            using (StreamWriter writer = new StreamWriter(targetPath, false))
            {
                foreach (string word in _vocab)
                {
                    writer.WriteLine(word);
                }
            }

            log.InfoFormat("Saved the vocabulary to {0}", targetPath);
        }
    }
}
