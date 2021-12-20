#SingleInstance Off

pid := A_Args[1]
keydelay := A_Args[2]
SetKeyDelay, %keydelay%

ControlSend, ahk_parent, {Blind}{Esc 2}{Tab 9}{Enter}, ahk_pid %pid%

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
