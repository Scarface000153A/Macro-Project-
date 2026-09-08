Set WshShell = CreateObject("WScript.Shell")
' Run Flask app in the background without any command prompt window
WshShell.Run "pythonw app.py", 0, False
WScript.Sleep 1000
' Open default browser
WshShell.Run "http://127.0.0.1:5000", 1, False
