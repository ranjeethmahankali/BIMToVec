using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

using Xbim.ModelGeometry.Scene;
using Xbim.ModelGeometry.Converter;
using Xbim.Ifc;

using Xbim.Common.Geometry;
using BIMToVecSampler.Samplers;

namespace BIMToVecSampler
{
    class Program
    {
        static void Main(string[] args)
        {
            if(args.Length == 0) { return; }
            string path = args[0];
            string[] files = Directory.GetFiles(path);

            foreach(string file in files)
            {
                string savePath = @"C:\Users\Ranjeeth Mahankali\Desktop\" + 
                    Path.ChangeExtension(Path.GetFileName(file), ".txt");

                SpatialTreeSampler spatial = new SpatialTreeSampler(file);
                SemanticTreeSampler semantic = new SemanticTreeSampler(file);

                spatial.SaveDatasetAsText(savePath);
                semantic.SaveDatasetAsText(savePath, true);
            }

            Console.Write("Press any key to continue...");
            Console.ReadKey();
        }
    }
}
