#SingleInstance Ignore

pid := A_Args[1]
title := A_Args[2]
WinSetTitle, ahk_pid %pid%, , %title%
Sleep, 1000
ExitApp