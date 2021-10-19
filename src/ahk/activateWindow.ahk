#Persistent
#WinActivateForce
WinSet, AlwaysOnTop, On, ahk_pid %pid%
Sleep, %switchDelay%
send {LButton}
WinMaximize, ahk_pid %pid%
WinSet, AlwaysOnTop, Off, ahk_pid %pid%
ExitApp