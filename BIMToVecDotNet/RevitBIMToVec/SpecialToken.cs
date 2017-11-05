using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Autodesk.Revit.UI;

namespace RevitBIMToVec
{
    public class IncomingToken
    {
        private static Dictionary<string, IncomingToken> _tokenDict = new Dictionary<string, IncomingToken>();
        #region-fields
        private string _name;
        private Action _bindingFunc;
        #endregion

        #region-properties
        public string Name
        {
            get { return _name; }
        }
        #endregion

        #region-constructors
        private IncomingToken(string name, Action func)
        {
            _name = name;
            _bindingFunc = func;
            if (_tokenDict.ContainsKey(_name))
            {
                throw new ArgumentException("A special token with that name already exists.");
            }
            _tokenDict.Add(_name, this);
        }
        #endregion

        #region-functions
        private static IncomingToken ByName(string name)
        {
            IncomingToken token = null;
            if (_tokenDict.TryGetValue(name, out token))
            {
                return token;
            }
            return null;
        }

        public static bool MatchAndExecuteToken(string name)
        {
            IncomingToken token = ByName(name);
            if(token == null)
            {
                return false;
            }
            else
            {
                token._bindingFunc.Invoke();
                return true;
            }
        }
        #endregion

        #region-static members
        private static readonly IncomingToken SERVER_ERROR = new IncomingToken(
            "error_ec995d88-ee8e-4288-a2da-3c93d231992b", () => {
                string errorMsg = RevitClient.ListenAndReturnData();
                TaskDialog box = new TaskDialog("Python Server Error");
                box.MainInstruction = "error message: ";
                box.MainContent = errorMsg;
                box.Show();
        });
        #endregion
    }

    public class OutgoingToken
    {
        public static readonly string STOP_SERVER = "stop_server_498994a4-24a1-4496-9a41-3e6f907d0ffa";
    }
}
