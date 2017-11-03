using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.Reflection;
using System.Diagnostics;

namespace RevitBIMToVec
{
    public class RevitClient
    {
        private static string _host = "127.0.0.1";
        private static int _outgoingPort = 5006;
        private static int _incomingPort = 5007;
        public static string _baseDir = @"C:\RevitBIMToVec";
        public static string _pythonServerFile = "model_server.py";
        private static Process _pythonServer;
        private static bool _pythonServerActive = false;

        public static bool PythonServerActive
        {
            get { return _pythonServerActive; }
            set { _pythonServerActive = false; }
        }

        static RevitClient()
        {
            string command = "python " + _pythonServerFile;
            _pythonServer = new Process();
            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.WorkingDirectory = _baseDir;
            startInfo.FileName = "cmd.exe";
            startInfo.Arguments = "/C " + command;
            _pythonServer.StartInfo = startInfo;
        }

        public static void SendData(string data)
        {
            TcpClient clientSocket = new TcpClient();
            clientSocket.Connect(_host, _outgoingPort);
            using (BinaryWriter writer = new BinaryWriter(clientSocket.GetStream()))
            {
                writer.Write(Encoding.ASCII.GetBytes(data));
            }
            clientSocket.Close();
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
            if (_pythonServerActive) { return; }
            _pythonServer.Start();
            _pythonServerActive = true;
        }

        public static void StopPythonServer()
        {
            if (!_pythonServerActive) { return; }
            SendData(OutgoingToken.STOP_SERVER);
            _pythonServer.WaitForExit();
            _pythonServer.Close();
            _pythonServerActive = false;
        }
    }
}
