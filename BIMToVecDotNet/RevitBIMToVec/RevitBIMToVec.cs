using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;

using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using System.IO.Pipes;
using System.IO;

namespace RevitBIMToVec
{
    [TransactionAttribute(TransactionMode.Manual)]
    [RegenerationAttribute(RegenerationOption.Manual)]
    public class RevitBIMToVec : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            string msg = "this is my message, I am Ranjeeth.";
            //ask user to select a bunch of items
            //get their material names, and ifc names
            //serialize the data into a string
            //send the data
            //receive the inference back from the server
            //deserialize the received inference appropriately
            //display a message window to show the user that inference.
            //incomplete
            return Result.Succeeded;
        }
    }
}
