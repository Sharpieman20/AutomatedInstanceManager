
multimcpid := A_Args[1]
multimcdelay := A_Args[2]
instname := A_Args[3]

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
MouseMove, 770, 440, 0
sleep, %multimcdelay%
Send, {Click 770, 440} ; Click copy instance
sleep, %multimcdelay%
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
sleep, %multimcdelay%
WinSet, AlwaysOnTop, On, Copy Instance
sleep, %multimcdelay%
Send, %instname% ; Type instance name
sleep, %multimcdelay%
Send, {Enter} ; Create instance
sleep, %multimcdelay%
