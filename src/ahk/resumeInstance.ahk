#SingleInstance Ignore

pid := A_Args[1]
hProcess := DllCall("OpenProcess", "UInt", 0x1F0FFF, "Int", 0, "Int", pid)
If (hProcess) {
  DllCall("ntdll.dll\NtResumeProcess", "Int", hProcess)
  DllCall("CloseHandle", "Int", hProcess)
}
Sleep, 1000
ExitApp