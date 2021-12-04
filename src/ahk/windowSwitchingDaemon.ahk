#Persistent

switchDelay := A_Args[1]
borderless := A_Args[2]
maximize := A_Args[3]
autoUnpause := A_Args[4]
playDelay := A_Args[5]
pipeFileLocation := A_Args[6]
loopDelay := A_Args[7]

oldInstance := -1
newInstance := -1

Loop
{
    Sleep %loopDelay%
    oldInstance := -1
    newInstance := -1
    index := 0
    Loop, read, %pipeFileLocation%
	{
        if (index = 0)
            oldInstance := A_LoopReadLine
        else
            newInstance := A_LoopReadLine
        index+=1
    }
    if (oldInstance != -1) {
        FileDelete, %pipeFileLocation%
        WinSet, AlwaysOnTop, Off, ahk_pid %oldInstance%
        if (maximize)
            WinMaximize, ahk_pid %newInstance%
        Sleep %maximizeDelay%
        WinSet, AlwaysOnTop, On, ahk_pid %newInstance%
        Sleep %switchDelay%
        send {LButton}
        if (autoUnpause)
            ControlSend, ahk_parent, {Esc}, ahk_pid %oldInstance%
        if (maximize)
            WinMaximize, ahk_pid %newInstance%
        if (borderless)
            WinSet, Style, -0xCF0000, ahk_pid %newInstance%
        oldInstance := -1
        newInstance := -1
    }
}
