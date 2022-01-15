#SingleInstance Off

pid := A_Args[1]
hProcess := DllCall("OpenProcess", "UInt", 0x1F0FFF, "Int", 0, "Int", pid)
DllCall("SetWindowPos", "UInt", hProcess, "UInt", 0, "Int", 0, "Int", -1000, "Int", 1920, "Int", 3080, "UInt", 0x0400)
DllCall("CloseHandle", "Int", hProcess)
If (hProcess) {
  DllCall("ntdll.dll\NtSuspendProcess", "Int", hProcess)
  DllCall("SetProcessWorkingSetSize", "UInt", hProcess, "Int", -1, "Int", -1)
  DllCall("CloseHandle", "Int", hProcess)
}
Sleep, 1000
ExitApp