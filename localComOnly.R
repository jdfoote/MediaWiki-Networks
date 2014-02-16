if (!"RSiena" %in% installed.packages()) install.packages("RSiena")
if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
require(RSiena)
require(sna)
require(network)

dichotCutoff = 2.9

lc1 <- event2dichot(as.matrix(read.table("2012_07_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc2 <- event2dichot(as.matrix(read.table("2012_08_02_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc3 <- event2dichot(as.matrix(read.table("2012_09_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc4 <- event2dichot(as.matrix(read.table("2012_10_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc5 <- event2dichot(as.matrix(read.table("2012_10_31_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc6 <- event2dichot(as.matrix(read.table("2012_11_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc7 <- event2dichot(as.matrix(read.table("2012_12_30_localComm.csv")),method="absolute", thresh=dichotCutoff)

activeDays <- as.matrix(read.table("_behavior.csv"))
activePeriods <- cut(activeDays, c(-1,0,5,10,20,30), labels=FALSE)
dim(activePeriods) <- c(463,7)

localCom <- sienaNet(array(c(lc1,lc2,lc3,lc4,lc5,lc6,lc7),dim=c(463,463,7)))

simpleActivity <- varCovar(simpleEdits)
daysActiveLevel <- sienaNet(activePeriods, type="behavior")

MyData <- sienaDataCreate(localCom, daysActiveLevel)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="localOnlyModel")

# Include network effects
#MyEffects <- includeEffects(MyEffects,transTrip,cycle3,name="observation")
MyEffects <- includeEffects(MyEffects, transTriads, name="localCom")

# Include Behavior effects
# MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="daysActiveLevel", name="observation")
MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="daysActiveLevel", name="localCom")

#MyEffects <- includeEffects(MyEffects, name = "daysActiveLevel", avAlt, indeg, outdeg, interaction1 = "observation")
MyEffects <- includeEffects(MyEffects, name = "daysActiveLevel", avAlt, indeg, outdeg, interaction1 = "localCom")

# Covar effects
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "simpleActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "simpleActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,X,name="observation",interaction1="localCom")
MyModel <-sienaModelCreate(projname = "localOnly", modelType = 5)
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=TRUE)

print(MyResults)
