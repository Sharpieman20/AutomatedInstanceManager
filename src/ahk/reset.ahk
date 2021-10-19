#Persistent
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Esc 2}{Tab 9}{Enter}, ahk_pid %pid%
WinHide, ahk_pid %pid%
ExitApp