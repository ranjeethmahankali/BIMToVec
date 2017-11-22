using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.IO;

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
        private static string _ifcMappingFileName = "exportlayers-ifc-IAI.txt";
        private static Dictionary<string, string> _ifcNameMap = new Dictionary<string, string>();
        internal static void LoadIfcNameMapping(string filePath = null)
        {
            filePath = filePath ?? Path.Combine(RevitClient._baseDir, _ifcMappingFileName);
            using(StreamReader reader = new StreamReader(filePath))
            {
                string line = null;
                while((line = reader.ReadLine()) != null)
                {
                    if (line.Contains('#')) { line = line.Substring(0, line.IndexOf('#')); }
                    var terms = line.Split('\t');
                    if(terms.Length < 3) { continue; }
                    if (_ifcNameMap.ContainsKey(terms[0]+terms[1]))
                    {
                        _ifcNameMap[terms[0] + terms[1]] = ProcessString(terms[2]);
                    }
                    else
                    {
                        _ifcNameMap.Add(terms[0] + terms[1], ProcessString(terms[2]));
                    }
                }
            }
        }

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

            List<string> words = new List<string>();
            foreach(var objRef in picked)
            {
                Element elem = doc.GetElement(objRef);
                string className;

                if (_ifcNameMap.TryGetValue(elem.Category.Name, out className) && !words.Contains(className))
                {
                    words.Add(className);
                }
                List<ElementId> matIds = elem.GetMaterialIds(true).ToList();
                matIds.AddRange(elem.GetMaterialIds(false).ToList());
                foreach( var id in matIds)
                {
                    string word = ProcessString(doc.GetElement(id).Name);
                    if (word == "") { continue; }
                    if (!words.Contains(word)) { words.Add(word); }
                }
            }

            string msg = String.Join(" ", words.ToArray());
            RevitClient.SendData(msg);
            string response = RevitClient.ListenAndReturnData();

            if (IncomingToken.MatchAndExecuteToken(response))
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
