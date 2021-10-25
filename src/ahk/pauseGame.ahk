pid := A_Args[1]
keydelay := A_Args[2]
SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{F3 Down}{Esc}{F3 Up}, ahk_pid %pid%