#SingleInstance Off

pid := A_Args[1]
hProcess := DllCall("OpenProcess", "UInt", 0x1F0FFF, "Int", 0, "Int", pid)
If (hProcess) {
  DllCall("ntdll.dll\NtResumeProcess", "Int", hProcess)
  DllCall("SetProcessWorkingSetSize", "UInt", hProcess, "Int", 2000000000, "Int", 2000000000)
  DllCall("CloseHandle", "Int", hProcess)
}
Sleep, 1000
ExitApp