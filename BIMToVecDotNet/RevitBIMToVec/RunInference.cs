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
using Autodesk.Revit.DB.IFC;
using Autodesk.Revit.DB.ExternalService;

namespace RevitBIMToVec
{
    [TransactionAttribute(TransactionMode.Manual)]
    [RegenerationAttribute(RegenerationOption.Manual)]
    public class RunInference : IExternalCommand
    {
        private List<Element> _pickedElements = new List<Element>();
        private List<string> _ifcNames = new List<string>();
 
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIApplication uiApp = commandData.Application;
            Document doc = uiApp.ActiveUIDocument.Document;
            Selection sel = uiApp.ActiveUIDocument.Selection;
            List<Reference> picked = sel.PickObjects(ObjectType.Element, "Select the objects that you want to group").ToList();

            foreach(var objRef in picked)
            {
                _pickedElements.Add(doc.GetElement(objRef));
            }

            string msg = "ifcdoor ifcstair ifcsite";
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
