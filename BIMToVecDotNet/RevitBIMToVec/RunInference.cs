using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;

namespace RevitBIMToVec
{
    [TransactionAttribute(TransactionMode.Manual)]
    [RegenerationAttribute(RegenerationOption.Manual)]
    public class RunInference : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            string msg = "this is my message, I am Ranjeeth.";
            RevitClient.SendData(msg);
            string response = RevitClient.ListenAndReturnData();

            TaskDialog box = new TaskDialog("Python Server");
            box.MainInstruction = "Hi Revit Client !";
            box.MainContent = "I am ready to serve python utilities including tensorflow.";
            box.Show();
            //RevitClient.SendData(msg);
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
