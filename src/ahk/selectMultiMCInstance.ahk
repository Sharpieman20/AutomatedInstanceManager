#SingleInstance, Force
SetKeyDelay, %keydelay%

Loop, %downarrows% {
  ControlSend,, {Down}, MultiMC
  sleep, 50
}
Loop, %rightarrows% {
  ControlSend,, {Right}, MultiMC
  sleep, 50
}