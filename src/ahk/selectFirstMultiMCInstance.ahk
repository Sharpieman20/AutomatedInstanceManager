
multimcpid := A_Args[1]
multimcdelay := A_Args[2]

SendMode Input
CoordMode, Mouse, Screen

WinMove, ahk_pid %multimcpid%,,0,0,640,640
sleep, %multimcdelay%
WinSet, AlwaysOnTop, On, ahk_pid %multimcpid%
sleep, %multimcdelay%
WinActivate, ahk_pid %multimcpid%
sleep, %multimcdelay%
MouseMove, 75, 10, 0
sleep, %multimcdelay%
Send, {Click 75, 10}
sleep, %multimcdelay%
MouseMove, 75, 150, 0
sleep, %multimcdelay%
Send, {Click 75, 150}
sleep, %multimcdelay%
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
sleep, %multimcdelay%
