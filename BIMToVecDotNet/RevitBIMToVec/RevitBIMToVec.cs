using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Reflection;
using System.Windows.Media.Imaging;

using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Architecture;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;

namespace RevitBIMToVec
{
    public class RevitBIMToVec : IExternalApplication
    {
        public string BaseDirectory
        {
            get { return RevitClient._baseDir; }
        }
        public Result OnShutdown(UIControlledApplication application)
        {
            RevitClient.StopPythonServer();
            return Result.Succeeded;
        }

        public Result OnStartup(UIControlledApplication application)
        {
            RibbonPanel panel = application.CreateRibbonPanel("RevitBIMToVec");
            string assemblyPath = Assembly.GetExecutingAssembly().Location;
            PushButtonData btnData = new PushButtonData("Inference", "Run Inference", assemblyPath, "RevitBIMToVec.RunInference");
            PushButton btn = panel.AddItem(btnData) as PushButton;
            btn.ToolTip = "Get Inference from the python server";

            BitmapImage image = new BitmapImage(new Uri(Path.Combine(BaseDirectory,"RevitBIMToVecLogo.png")));
            btn.LargeImage = image;

            RunInference.LoadIfcNameMapping();

            try
            {
                RevitClient.StartPythonServer();
            }
            catch(Exception e)
            {
                TaskDialog box = new TaskDialog("Python Server");
                box.MainInstruction = "Error!";
                box.MainContent = "Failed to start the Python server:\n"+e.Message;
                box.Show();
                return Result.Failed;
            }
            return Result.Succeeded;
        }
    }
}
