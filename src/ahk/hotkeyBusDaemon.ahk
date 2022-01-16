#SingleInstance Force

SendMode Input

logDir := A_Args[1]
loopDelay := A_Args[2]
inputPipeFileLocation := A_Args[3]

OutInd := 0

LogOutInput(KeyInput)
{
    Critical, On
    MyInd := OutInd
    OutInd := OutInd + 1
    Critical, Off
    FilName := %logDir%\%MyInd%.aim.out
    OutFilName := %logDir%\%MyInd%.aim.in
    FileAppend, %KeyInput%, %FilName%
    FileMove, %FilName%, %OutFileName%
    return
}

Loop
{
    Sleep %loopDelay%
    pid := -1
    key := Null
    index := 0
    Loop, read, %inputPipeFileLocation%
	{
        if (index = 0)
            pid := A_LoopReadLine
        else
            key := A_LoopReadLine
        index+=1
    }
    if (pid != -1) {
        FileDelete, %inputPipeFileLocation%
        ControlSend, {%key%}, ahk_parent %pid%
    }
}

