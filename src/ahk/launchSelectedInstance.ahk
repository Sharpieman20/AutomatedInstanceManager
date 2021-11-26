
multimcpid := A_Args[1]
multimcdelay := A_Args[2]

SendMode Input
CoordMode, Mouse, Screen

WinMove, ahk_pid %multimcpid%,,0,0,640,640
sleep, %multimcdelay%
WinSet, AlwaysOnTop, On, ahk_pid %multimcpid%
sleep, %multimcdelay%
MouseMove, 770, 480, 0
sleep, %multimcdelay%
Send, {Click 770, 480} ; Click to activate the window
sleep, %multimcdelay%
MouseMove, 770, 225, 0
sleep, %multimcdelay%
Send, {Click 770, 225} ; Click to activate the window
sleep, %multimcdelay%
Send, {Enter}
sleep, %multimcdelay%
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
sleep, %multimcdelay%
