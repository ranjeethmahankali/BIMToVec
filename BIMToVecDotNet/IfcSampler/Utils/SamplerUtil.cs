using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows.Forms;
using System.Text.RegularExpressions;
using Xbim.Common.Geometry;


namespace IfcSampler.Utils
{
    public class SamplerUtil
    {
        public static bool Equals(double a, double b, double tolerance = 0.001)
        {
            return Math.Abs(a - b) <= tolerance;
        }

        //returns the highest of the numbers given
        public static double Max(params double[] nums)
        {
            double max = double.MinValue;
            foreach (double num in nums)
            {
                if (num > max) { max = num; }
            }

            return max;
        }

        public static bool BBoxEqual(XbimRect3D a, XbimRect3D b, double tolerance = 0.001)
        {
            return Equals(a.X, b.X, tolerance)
                && Equals(a.Y, b.Y, tolerance)
                && Equals(a.Z, b.Z, tolerance)
                && Equals(a.SizeX, b.SizeX, tolerance)
                && Equals(a.SizeY, b.SizeY, tolerance)
                && Equals(a.SizeZ, b.SizeZ, tolerance);
        }

        public static string GetAbsoluteFilePath(string filePath)
        {
            return Path.IsPathRooted(filePath) ? filePath : Path.Combine(Application.StartupPath, filePath);
        }
        public static bool IsValidIfcFile(string filePath)
        {
            return File.Exists(filePath) &&
                Path.ChangeExtension(Path.GetFileName(filePath), GlobalVariables.DataFileExtension) != GlobalVariables.VOCAB_SAVE_FILENAME;
        }

        public static bool IsValidDirectory(string path)
        {
            FileAttributes attr = File.GetAttributes(path);
            return attr.HasFlag(FileAttributes.Directory) && (!Directory.Exists(path));
        }

        public static List<List<T>> PartitionList<T>(List<T> list, int maxSize)
        {
            List<List<T>> partitions = new List<List<T>>();
            int i = 0;
            while (i < list.Count)
            {
                int offset = Math.Min(maxSize, list.Count - i);
                partitions.Add(list.GetRange(i, offset));
                i += offset;
            }

            return partitions;
        }

        public static string ProcessString(string word)
        {
            Regex rgx = new Regex("[^a-z]");
            string result = rgx.Replace(word.ToLower(), "");
            if(word.ToLower() != result)
            {

            }
            return result;
        }

        public static void ProcessCollection(ref List<string> words)
        {
            for(int i = 0; i < words.Count; i++)
            {
                words[i] = ProcessString(words[i]);
            }
        }
    }
}
