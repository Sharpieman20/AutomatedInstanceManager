keydelay := A_Args[1]
downarrows := A_Args[2]
rightarrows := A_Args[3]

SetKeyDelay, %keydelay%

Loop, %downarrows% {
  ControlSend,, {Down}, MultiMC
  sleep, 50
}
Loop, %rightarrows% {
  ControlSend,, {Right}, MultiMC
  sleep, 50
}