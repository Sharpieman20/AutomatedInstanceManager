multimcpid := A_Args[1]
keydelay := A_Args[2]
downarrows := A_Args[3]
rightarrows := A_Args[4]

SetKeyDelay, 100

Loop, %downarrows% {
  ControlSend,, {Down}, ahk_pid %multimcpid%
  sleep, 200
}
Loop, %rightarrows% {
  ControlSend,, {Right}, ahk_pid %multimcpid%
  sleep, 200
}