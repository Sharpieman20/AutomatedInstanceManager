
multimcpid := A_Args[1]
keydelay := A_Args[2]
instname := A_Args[3]

SendMode Input
CoordMode, Mouse, Screen
SetKeyDelay, %keydelay%

WinSet, AlwaysOnTop, On, ahk_pid %multimcpid%
sleep, 50
WinMove, ahk_pid %multimcpid%,,0,0,640,640
sleep, 50
MouseMove, 770, 440, 0
sleep, 2000
Send, {Click 770, 440} ; Click copy instance
sleep, 2000
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
sleep, 50
WinSet, AlwaysOnTop, On, Copy Instance
sleep, 50
Send, %instname% ; Type instance name
sleep, 100
Send, {Enter} ; Create instance