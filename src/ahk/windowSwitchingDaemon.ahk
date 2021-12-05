#SingleInstance Force

ConsolePrint(ByRef vText:="")
{
	static vIsReady := 0, oStdOut
	if !vIsReady
	{
		DllCall("kernel32\AllocConsole")
		oStdOut := FileOpen("*", "w `n")
		vIsReady := 1
	}
	oStdOut.Write(vText)
	oStdOut.Read(0) ;flush the write buffer
}

ConsolePrintLine(ByRef vText:="")
{
	ConsolePrint(vText)
	ConsolePrint("`n")
}

switchDelay := A_Args[1]
borderless := A_Args[2]
maximize := A_Args[3]
autoUnpause := A_Args[4]
playDelay := A_Args[5]
pipeFileLocation := A_Args[6]
loopDelay := A_Args[7]

ConsolePrintLine("read args")

oldInstance := -1
newInstance := -1

Loop
{
    ConsolePrintLine("loop")
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
        ConsolePrintLine("do switch")
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
