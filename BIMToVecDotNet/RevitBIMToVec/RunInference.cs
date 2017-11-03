using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
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
        public static string ProcessString(string word)
        {
            Regex rgx = new Regex("[^a-z]");
            string result = rgx.Replace(word.ToLower(), "");
            return result;
        }

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            UIApplication uiApp = commandData.Application;
            Document doc = uiApp.ActiveUIDocument.Document;
            Selection sel = uiApp.ActiveUIDocument.Selection;
            List<Reference> picked = sel.PickObjects(ObjectType.Element, "Select the objects that you want to group").ToList();

            List<string> matNames = new List<string>();
            foreach(var objRef in picked)
            {
                Element elem = doc.GetElement(objRef);
                var matIds = elem.GetMaterialIds(true);
                foreach( var id in matIds)
                {
                    string word = ProcessString(doc.GetElement(id).Name);
                    if (word == "") { continue; }
                    matNames.Add(word);
                }
            }

            string msg = String.Join(" ", matNames.ToArray());
            RevitClient.SendData(msg);
            string response = RevitClient.ListenAndReturnData();

            if (SpecialToken.MatchAndExecuteToken(response))
            {
                return Result.Succeeded;
            }

            TaskDialog box = new TaskDialog("Python Server");
            box.MainInstruction = "Odd one out: ";
            box.MainContent = response;
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
