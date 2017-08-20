using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows.Forms;

using Xbim.Common.Logging;
using BIMToVecSampler.Samplers;

namespace BIMToVecSampler
{
    class Program
    {
        private static readonly ILogger log = LoggerFactory.GetLogger();
        static void Main(string[] args)
        {
            if(args.Length != 2)
            {
                string p1 = "The directory containing all the ifc files";
                string p2 = "The directory to which the dataset should be saved";
                log.FatalFormat("The sampler expects exactly two arguments:\n\t{0}\n\t{1}",p1, p2);
                Console.Write("Now exiting. Press any key to continue...");
                Console.ReadKey();
                return;
            }
            //checking if the user provided relative or absolute paths and dealing with that appropriately
            for(int i = 0; i < args.Length; i++)
            {
                if (!Path.IsPathRooted(args[i]))
                {
                    args[i] = Path.Combine(Application.StartupPath, args[i]);
                }
            }
            string path = args[0];
            string datasetPath = args[1];

            string[] files = Directory.GetFiles(path);
            for (int i = 0; i < files.Length; i++)
            {
                SpatialTreeSampler spatial = new SpatialTreeSampler(files[i], datasetPath);
                SemanticTreeSampler semantic = new SemanticTreeSampler(files[i], datasetPath);
                spatial.ExportDatasetAsText(i == 0);//if i == 0 we clean up the dataset folder
                semantic.ExportDatasetAsText();
            }

            Console.Write("Press any key to continue...");
            Console.ReadKey();
        }
    }
}
