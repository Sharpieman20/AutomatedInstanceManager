
keydelay := A_Args[1]
instname := A_Args[2]

SendMode Input
CoordMode, Mouse, Screen
SetKeyDelay, %keydelay%

WinSet, AlwaysOnTop, On, MultiMC
sleep, 50
WinMove, MultiMC,,0,0,640,640
sleep, 50
Send, {Click 580, 580} ; Click copy instance
sleep, 50
WinSet, AlwaysOnTop, Off, MultiMC
WinSet, AlwaysOnTop, On, Copy Instance
sleep, 50
Send, %instname% ; Type instance name
sleep, 100
Send, {Enter} ; Create instance