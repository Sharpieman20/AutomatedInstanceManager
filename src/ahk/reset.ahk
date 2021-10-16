#Persistent
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Esc}{Tab 9}{Enter}, ahk_pid %pid%
ExitApp