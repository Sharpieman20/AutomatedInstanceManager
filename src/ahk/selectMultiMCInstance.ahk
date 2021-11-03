keydelay := A_Args[1]
downarrows := A_Args[2]
rightarrows := A_Args[3]

SetKeyDelay, %keydelay%

Loop, %downarrows% {
  ControlSend,, {Down}, MultiMC
  sleep, 200
}
Loop, %rightarrows% {
  ControlSend,, {Right}, MultiMC
  sleep, 200
}