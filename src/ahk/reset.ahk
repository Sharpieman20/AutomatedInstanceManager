#SingleInstance Off

pid := A_Args[1]
keydelay := A_Args[2]

SetKeyDelay, %keydelay%

ControlSend, ahk_parent, {Blind}{Esc}, ahk_pid %pid
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Esc}, ahk_pid %pid
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Shift down}{Tab}{Shift up}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Enter}, ahk_pid %pid%

Sleep, 1000
ExitApp
