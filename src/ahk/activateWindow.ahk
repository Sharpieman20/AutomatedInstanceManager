pid := A_Args[1]
switchDelay := A_Args[2]
borderless := A_Args[3]
maximize := A_Args[4]
keepOnTop := A_Args[5]
if (%maximize%) {
    WinMaximize, ahk_pid %pid%
}
WinSet, AlwaysOnTop, On, ahk_pid %pid%
Sleep, %switchDelay%
send {LButton}
if (%keepOnTop%) {

} else {
    WinSet, AlwaysOnTop, Off, ahk_pid %pid%
}
if (%borderless%) {
    WinSet, Style, -0xCF0000, ahk_pid %pid%
}