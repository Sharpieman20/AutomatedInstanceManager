pid := A_Args[1]
keydelay := A_Args[2]
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab 8}{Enter}, ahk_pid %pid%