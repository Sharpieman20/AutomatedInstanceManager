#SingleInstance Off

SendMode Input

pid := A_Args[1]
keydelay := A_Args[2]

SetKeyDelay, -1

ControlSend, ahk_parent, {Blind}{Esc}, ahk_pid %pid
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Esc}, ahk_pid %pid
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab}, ahk_pid %pid%
Sleep, %keydelay%
ControlSend, ahk_parent, {Blind}{Enter}, ahk_pid %pid%

Sleep, 1000
ExitApp
