using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Autodesk.Revit.UI;

namespace RevitBIMToVec
{
    public class SpecialToken
    {
        private static Dictionary<string, SpecialToken> _tokenDict = new Dictionary<string, SpecialToken>();
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
        private SpecialToken(string name, Action func)
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
        private static SpecialToken ByName(string name)
        {
            SpecialToken token = null;
            if (_tokenDict.TryGetValue(name, out token))
            {
                return token;
            }
            return null;
        }

        public static bool MatchAndExecuteToken(string name)
        {
            SpecialToken token = ByName(name);
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
        private static readonly SpecialToken SERVER_ERROR = new SpecialToken(
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
