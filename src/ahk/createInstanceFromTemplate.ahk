
keydelay := A_Args[1]
instname := A_Args[2]

SendMode Input
CoordMode, Mouse, Screen
SetKeyDelay, %keydelay%

WinSet, AlwaysOnTop, On, MultiMC
sleep, 50
WinMove, MultiMC,,0,0,640,640
sleep, 50
MouseMove, 770, 440, 0
sleep, 2000
Send, {Click 770, 440} ; Click copy instance
sleep, 2000
WinSet, AlwaysOnTop, Off, MultiMC
sleep, 50
WinSet, AlwaysOnTop, On, Copy Instance
sleep, 50
Send, %instname% ; Type instance name
sleep, 100
Send, {Enter} ; Create instance