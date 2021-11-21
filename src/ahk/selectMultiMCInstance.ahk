
multimcpid := A_Args[1]
multimcdelay := A_Args[2]
downarrows := A_Args[3]
rightarrows := A_Args[4]

SendMode Input

SetKeyDelay, 100

Loop, %downarrows% {
  ControlSend,, {Down}, ahk_pid %multimcpid%
  sleep, %multimcdelay%
}
Loop, %rightarrows% {
  ControlSend,, {Right}, ahk_pid %multimcpid%
  sleep, %multimcdelay%
}
