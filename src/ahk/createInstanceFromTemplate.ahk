#SingleInstance, Force
SendMode Input
CoordMode, Mouse, Screen
SetKeyDelay, %keydelay%

WinActivate, MultiMC
WinMove, A,,0,0,640,640
Send, {Click 75, 150} ;
sleep, 50
Send, {Click 580, 580} ; Click copy instance
sleep, 50
Send, %instname% ; Type instance name
sleep, 100
Send, {Enter} ; Create instance