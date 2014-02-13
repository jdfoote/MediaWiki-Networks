#TODO: Make observation a dyadic covar (per the manual)? If so, figure out what measures to add (interaction between that and dependent var).

if (!"RSiena" %in% installed.packages()) install.packages(RSiena)
if (!"sna" %in% installed.packages()) install.packages(sna)
if (!"network" %in% installed.packages()) install.packages(network)
require(RSiena)
require(sna)
require(network)

dichotCutoff = 1.9

o1 <- event2dichot(as.matrix(read.table("2012_07_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o2 <- event2dichot(as.matrix(read.table("2012_08_02_observation.csv")),method="absolute", thresh=dichotCutoff)
o3 <- event2dichot(as.matrix(read.table("2012_09_01_observation.csv")),method="absolute", thresh=dichotCutoff)
lc1 <- event2dichot(as.matrix(read.table("2012_07_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc2 <- event2dichot(as.matrix(read.table("2012_08_02_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc3 <- event2dichot(as.matrix(read.table("2012_09_01_localComm.csv")),method="absolute", thresh=dichotCutoff)

activeDays <- as.matrix(read.table("_behavior.csv"))
activePeriods <- cut(activeDays, c(-1,0,5,10,20,30), labels=FALSE)
dim(activePeriods) <- c(463,7)
print(activePeriods)

simpleEdits <- as.matrix(read.table("simple_edits_attributes.csv"))[,1:2]

observation <- sienaNet(array(c(o1,o2,o3),dim=c(463,463,3)))
localCom <- sienaNet(array(c(lc1,lc2,lc3),dim=c(463,463,3)))

simpleActivity <- varCovar(simpleEdits)
daysActiveLevel <- sienaNet(activePeriods[,1:3], type="behavior")

#MyData <- sienaDataCreate(observation, overallActivity, overallPlaceActivity, recentAllActivity, recentPlaceActivity)
MyData <- sienaDataCreate(observation, localCom, daysActiveLevel, simpleActivity)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="activityLevelTest")

# Include network effects
MyEffects <- includeEffects(MyEffects,transTrip,cycle3,name="observation")
MyEffects <- includeEffects(MyEffects,transTrip,cycle3,name="localCom")

# Include Behavior effects
MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="daysActiveLevel", name="observation")
MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="daysActiveLevel", name="localCom")

MyEffects <- includeEffects(MyEffects, name = "daysActiveLevel", avAlt, indeg, outdeg, interaction1 = "observation")
MyEffects <- includeEffects(MyEffects, name = "daysActiveLevel", avAlt, indeg, outdeg, interaction1 = "localCom")

# Covar effects
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "simpleActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "simpleActivity", name="localCom")

#MyEffects <- includeEffects(MyEffects,X,name="observation",interaction1="localCom")
MyModel <-sienaModelCreate(projname = "MyResults")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=TRUE)

print(MyResults)
