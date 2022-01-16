#SingleInstance Force

LogDir := A_Args[1]

Ind := 0

LogOutInput(KeyInput)
{
    Critical, On
    Ind := Ind + 1
    Critical, Off
    FilName := LogDir\%Ind%.aim.out
    OutFilName := LogDir\%Ind%.aim.in
    FileAppend, %KeyInput%, %FilName%
    FileMove, %FilName%, %OutFileName%
    return
}


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
    if (newInstance != -1) {
        FileDelete, %pipeFileLocation%
        WinSet, AlwaysOnTop, Off, ahk_pid %oldInstance%
        if (maximize)
            WinMaximize, ahk_pid %newInstance%
        Sleep, %maximizeDelay%
        WinSet, AlwaysOnTop, On, ahk_pid %newInstance%
        Sleep, %switchDelay%
        send {LButton}
        if (%autoUnpause%)
            ControlSend, ahk_parent, {Esc}, ahk_pid %oldInstance%
        if (%maximize%)
            WinMaximize, ahk_pid %newInstance%
        if (%borderless%)
            WinSet, Style, -0xCF0000, ahk_pid %newInstance%
        WinSet, AlwaysOnTop, Off, ahk_pid %newInstance%
    }
}
