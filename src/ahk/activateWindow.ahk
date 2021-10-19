#Persistent
#WinActivateForce
WinSet, AlwaysOnTop, On, ahk_pid %pid%
Sleep, %switchDelay%
send {LButton}
WinSet, AlwaysOnTop, Off, ahk_pid %pid%
ExitApp