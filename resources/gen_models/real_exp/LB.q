Pr[<=90;10](<> scs)
simulate[<=90;1]{scs, served[0],  humanPositionX[currH-1]/100, humanPositionY[currH-1]/100, robPositionX[currR-1]/100, robPositionY[currR-1]/100, dX[currR-1]/100, dY[currR-1]/100, PATH}
E[<=90](max:humanFatigue[0])
E[<=90](min:batteryCharge[0])
