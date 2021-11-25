pid := A_Args[1]
isMaximized := A_Args[2]
fullscreen := A_Args[3]
fullscreenDelay := A_Args[4]
WinSet, AlwaysOnTop, Off, ahk_pid %pid%
if (%isMaximized%) {
    WinRestore, ahk_pid %pid%
}
if (%fullscreen%) {
    ControlSend, ahk_parent, {Blind}{F11}, ahk_pid %pid%
    sleep, %fullscreenDelay%
}
Sleep, 1000
ExitApp