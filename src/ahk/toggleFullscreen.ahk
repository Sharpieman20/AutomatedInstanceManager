#SingleInstance Ignore

pid := A_Args[1]
WinMaximize, ahk_pid %pid%
Sleep, 1000
ExitApp