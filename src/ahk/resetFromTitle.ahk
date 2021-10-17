#Persistent
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab 8}{Enter}, ahk_pid %pid%
ExitApp