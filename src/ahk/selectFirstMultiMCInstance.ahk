
multimcpid := A_Args[1]
multimcdelay := A_Args[2]

SendMode Input
CoordMode, Mouse, Screen

WinMove, ahk_pid %multimcpid%,,0,0,640,640
Sleep, %multimcdelay%
WinSet, AlwaysOnTop, On, ahk_pid %multimcpid%
Sleep, %multimcdelay%
WinActivate, ahk_pid %multimcpid%
Sleep, %multimcdelay%
MouseMove, 75, 10, 0
Sleep, %multimcdelay%
Send, {Click 75, 10}
Sleep, %multimcdelay%
MouseMove, 75, 150, 0
Sleep, %multimcdelay%
Send, {Click 75, 150}
Sleep, %multimcdelay%
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
Sleep, %multimcdelay%
ExitApp
