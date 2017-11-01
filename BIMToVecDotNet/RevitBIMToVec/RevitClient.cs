using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.Reflection;

namespace RevitBIMToVec
{
    public class RevitClient
    {
        private static string _host = "127.0.0.1";
        private static int _outgoingPort = 15555;
        private static int _incomingPort = 15556;
        public static string _baseDir = @"C:\RevitBIMToVec";
        public static string _pythonServerFile = "model_server.py";

        public static void SendData(string data)
        {
            TcpClient clientSocket = new TcpClient();
            clientSocket.Connect(_host, _outgoingPort);
            using (BinaryWriter writer = new BinaryWriter(clientSocket.GetStream()))
            {
                writer.Write(Encoding.ASCII.GetBytes(data));
            }
        }

        public static string ListenAndReturnData()
        {
            TcpListener listener = new TcpListener(IPAddress.Parse(_host), _incomingPort);
            listener.Start();
            TcpClient client = listener.AcceptTcpClient();
            NetworkStream nwStr = client.GetStream();
            byte[] received = new byte[client.ReceiveBufferSize];
            int bytesRead = nwStr.Read(received, 0, client.ReceiveBufferSize);
            string resp = Encoding.ASCII.GetString(received, 0, bytesRead);
            client.Close();
            listener.Stop();

            return resp;
        }

        public static void StartPythonServer(bool returnOutput = false,
            Action<string> stdoutProcessor = null, Action<string> stderrProcessor = null)
        {
            string command = "python " + _pythonServerFile;
            System.Diagnostics.Process process = new System.Diagnostics.Process();
            System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();
            startInfo.WorkingDirectory = _baseDir;
            startInfo.FileName = "cmd.exe";
            startInfo.Arguments = "/C " + command;
            //startInfo.CreateNoWindow = true;
            process.StartInfo = startInfo;
            process.Start();
        }
    }
}
