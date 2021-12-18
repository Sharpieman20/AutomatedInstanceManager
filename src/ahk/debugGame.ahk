#SingleInstance Off

pid := A_Args[1]
ControlSend, ahk_parent, {Blind}{F3 Down}{Shift}{F3 Up}, ahk_pid %pid%
Sleep, 1000
ExitApp
