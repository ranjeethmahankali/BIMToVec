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
            TcpClient clientSocket = new TcpClient();
            clientSocket.Connect("127.0.0.1", 15555);
            using(BinaryWriter writer = new BinaryWriter(clientSocket.GetStream()))
            {
                writer.Write(System.Text.Encoding.ASCII.GetBytes(msg));
            }

            TcpListener listener = new TcpListener(IPAddress.Parse("127.0.0.1"), 15556);
            listener.Start();
            TcpClient client = listener.AcceptTcpClient();
            NetworkStream nwStr = client.GetStream();
            byte[] received = new byte[client.ReceiveBufferSize];
            int bytesRead = nwStr.Read(received, 0, client.ReceiveBufferSize);
            string resp = Encoding.ASCII.GetString(received,0,bytesRead);

            return Result.Succeeded;
        }
    }
}
