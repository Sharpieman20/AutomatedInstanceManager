#SingleInstance Off

pid := A_Args[1]
instnum := A_Args[2]
loops := A_Args[3]
keydelay := A_Args[4]
  
loop, loops {
    WinSetTitle, ahk_pid %pid%, , Minecraft* 1.16.1 - Instance %instnum%
    Sleep, 50
}

SetKeyDelay, %keydelay%
ControlSend, ahk_parent, {Blind}{Tab 8}{Enter}, ahk_pid %pid%
Sleep, 1000
ExitApp
