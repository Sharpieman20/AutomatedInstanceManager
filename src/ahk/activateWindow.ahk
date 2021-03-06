pid := A_Args[1]
switchDelay := A_Args[2]
borderless := A_Args[3]
maximize := A_Args[4]
keepOnTop := A_Args[5]
autoUnpause := A_Args[6]
fullscreen := A_Args[7]
fullscreenDelay := A_Args[8]
WinSet, AlwaysOnTop, On, ahk_pid %pid%
Sleep, %switchDelay%
send {LButton}
if (%autoUnpause%) {
    ControlSend, ahk_parent, {Esc}, ahk_pid %pid%
}
if (%keepOnTop%) {

} else {
    WinSet, AlwaysOnTop, Off, ahk_pid %pid%
}
if (%borderless%) {
    WinSet, Style, -0xCF0000, ahk_pid %pid%
}
if (%maximize%) {
    WinMaximize, ahk_pid %pid%
}
if (%fullscreen%) {
    ControlSend, ahk_parent, {Blind}{F11}, ahk_pid %pid%
    sleep, %fullscreenDelay%
}
Sleep, 1000
ExitApp