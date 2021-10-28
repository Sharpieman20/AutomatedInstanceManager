pid := A_Args[1]
isMaximized := A_Args[2]
if (%isMaximized%) {
    WinRestore, ahk_pid %pid%
}
WinSet, AlwaysOnTop, Off, ahk_pid %pid%