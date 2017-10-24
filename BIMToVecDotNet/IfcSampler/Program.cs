using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Windows.Forms;
using System.Globalization;

using Xbim.Common.Logging;
using BIMToVecSampler.Samplers;

namespace BIMToVecSampler
{
    class Program
    {
        private static readonly ILogger log = LoggerFactory.GetLogger();
        static void Main(string[] args)
        {
            if(args.Length < 2 || args.Length > 3)
            {
                string p1 = "The directory containing all the ifc files";
                string p2 = "The directory to which the dataset should be saved";
                log.FatalFormat("The sampler expects exactly two arguments:\n\t{0}\n\t{1}",p1, p2);
                Console.Write("Now exiting. Press any key to continue...");
                Console.ReadKey();
                return;
            }
            int maxCountPerFile = GlobalVariables.DEFAULT_MAX_COUNT_PERFILE;
            if (args.Length == 3)
            {
                int count;
                if(int.TryParse(args[2],out count))
                {
                    maxCountPerFile = count;
                }
            }

            Dataset dSet = new Dataset(args[0], args[1]);
            dSet.Clear();
            dSet.AddSampler(new MaterialSampler());
            dSet.AddSampler(new SpatialTreeSampler());
            dSet.AddSampler(new SemanticTreeSampler());
            dSet.MaxDataCountPerFile = maxCountPerFile;

            dSet.ExportData();
            Console.Write("Finished. Press any key to continue...");
            Console.ReadKey();
        }
    }
}
