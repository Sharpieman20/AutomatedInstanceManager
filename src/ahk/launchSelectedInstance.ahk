#SingleInstance, Force
SendMode Input
CoordMode, Mouse, Screen
SetKeyDelay, %keydelay%

WinActivate, MultiMC
WinMove, A,,0,0,640,400
Send, {Click 75, 150} ;
sleep, 10
Send, {Enter} ; Launch instance