#SingleInstance Off

pid := A_Args[1]
keydelay := A_Args[2]
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Raw}{Esc 2}{Tab 9}{Enter}, ahk_pid %pid%
Sleep, 1000
ExitApp
