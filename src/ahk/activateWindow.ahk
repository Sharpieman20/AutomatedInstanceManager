#Persistent
if (%maximize%) {
    WinMaximize, ahk_pid %pid%
}
WinSet, AlwaysOnTop, On, ahk_pid %pid%
Sleep, %switchDelay%
send {LButton}
WinSet, AlwaysOnTop, Off, ahk_pid %pid%
if (%borderless%) {
    WinSet, Style, -0xCF0000, ahk_pid %pid%
}
ExitApp