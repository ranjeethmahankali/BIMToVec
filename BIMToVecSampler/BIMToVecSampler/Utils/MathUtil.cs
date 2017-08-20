using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xbim.Common.Geometry;

namespace BIMToVecSampler.Utils
{
    public class MathUtil
    {
        public static bool Equals(double a, double b, double tolerance = 0.001)
        {
            return Math.Abs(a - b) <= tolerance;
        }

        //returns the highest of the numbers given
        public static double Max(params double[] nums)
        {
            double max = double.MinValue;
            foreach(double num in nums)
            {
                if(num > max) { max = num; }
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
    }
}
