multimcpid = A_Args[1]

sleep, 500
WinSet, AlwaysOnTop, On, ahk_pid %multimcpid%
WinMove, ahk_pid %multimcpid%,,0,0,640,640 ;
sleep, 500
MouseMove, 75, 150, 0
sleep, 1000
Send, {Click 75, 150} ;
sleep, 1000
WinSet, AlwaysOnTop, Off, ahk_pid %multimcpid%
sleep, 50