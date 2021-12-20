#SingleInstance Off

pid := A_Args[1]
keydelay := A_Args[2]
pausedelay := A_Args[3]

Sleep, %pausedelay%
SetKeyDelay, %keydelay%

ControlSend, ahk_parent, {Blind}{F3 Down}{Esc}{F3 Up}, ahk_pid %pid%

Sleep, 10
If (not GetKeyState("Ctrl","P"))
{
    Send, {Blind}{Control Up}
}
if (not GetKeyState("Shift","P"))
{
    Send, {Blind}{Shift Up}
}


Sleep, 1000
ExitApp
