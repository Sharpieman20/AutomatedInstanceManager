#SingleInstance Off

pid := A_Args[1]
keydelay := A_Args[2]
pausedelay := A_Args[3]

Sleep, %pausedelay%

SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Raw}{F3 Down}{Esc}{F3 Up}, ahk_pid %pid%
Sleep, 1000
ExitApp
