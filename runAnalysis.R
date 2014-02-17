#TODO: Make observation a dyadic covar (per the manual)? If so, figure out what measures to add (interaction between that and dependent var).

if (!"RSiena" %in% installed.packages()) install.packages("RSiena")
if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
require(RSiena)
require(sna)
require(network)

dichotCutoff = 1.9

o1 <- event2dichot(as.matrix(read.table("2012_07_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o2 <- event2dichot(as.matrix(read.table("2012_08_02_observation.csv")),method="absolute", thresh=dichotCutoff)
o3 <- event2dichot(as.matrix(read.table("2012_09_01_observation.csv")),method="absolute", thresh=dichotCutoff)
o4 <- event2dichot(as.matrix(read.table("2012_10_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc1 <- event2dichot(as.matrix(read.table("2012_07_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc2 <- event2dichot(as.matrix(read.table("2012_08_02_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc3 <- event2dichot(as.matrix(read.table("2012_09_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc4 <- event2dichot(as.matrix(read.table("2012_10_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc5 <- event2dichot(as.matrix(read.table("2012_10_31_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc6 <- event2dichot(as.matrix(read.table("2012_11_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc7 <- event2dichot(as.matrix(read.table("2012_12_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
gc1 <- event2dichot(as.matrix(read.table("2012_07_03_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc2 <- event2dichot(as.matrix(read.table("2012_08_02_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc3 <- event2dichot(as.matrix(read.table("2012_09_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc4 <- event2dichot(as.matrix(read.table("2012_10_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)

activeDays <- as.matrix(read.table("_behavior.csv"))
activePeriods <- cut(activeDays, c(-1,0,5,10,20,30), labels=FALSE)
dim(activePeriods) <- c(463,7)

complexEdits <- as.matrix(read.table("complex_edits_attributes.csv"))[,1:3]
allActivity <- as.matrix(read.table("all_edits_attributes.csv"))[,1:3]
#communityEdits <- as.matrix(read.table("community_edits_attributes.csv"))[,1:3]
communityTalkEdits <- as.matrix(read.table("community_talk_edits_attributes.csv"))[,1:3]
localTalkEdits <- as.matrix(read.table("local_talk_edits_attributes.csv"))[,1:3]

daysSinceJoiningFile <- as.matrix(read.table("daysSinceJoining.csv"))[,1]

observation <- sienaNet(array(c(o2,o3,o4),dim=c(463,463,4)))
localCom <- sienaNet(array(c(lc1,lc2,lc3,lc4),dim=c(463,463,4)))
#globalCom <- sienaNet(array(c(gc1,gc2,gc3,gc4),dim=c(463,463,4)))

loggedActivity <- varCovar(log(allActivity+1))
complexActivity <- varCovar(complexEdits)
#communityActivity <- varCovar(communityEdits)
#communityTalkActivity <- varCovar(communityTalkEdits)
#localTalkActivity <- varCovar(localTalkEdits)

daysSinceJoining <- coCovar(daysSinceJoiningFile)

activityBeh <- sienaNet(activePeriods[,1:4], type="behavior")

MyData <- sienaDataCreate(localCom, activityBeh, loggedActivity, daysSinceJoining, complexActivity)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="activityLevelTest")

# Include network effects
#MyEffects <- includeEffects(MyEffects,transTrip,cycle3,outRate,name="observation")
#MyEffects <- includeEffects(MyEffects,outRate, name="observation",type="rate")
MyEffects <- includeEffects(MyEffects, transTriads, balance,name="localCom")

# Include Behavior effects
#MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="activityBeh", name="observation")
MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="activityBeh", name="localCom")

#MyEffects <- includeEffects(MyEffects, name = "activityBeh", avAlt, indeg, outdeg, interaction1 = "observation")
MyEffects <- includeEffects(MyEffects, name = "activityBeh", avAlt, interaction1 = "localCom")
#MyEffects <- includeEffects(MyEffects, name = "activityBeh", avAlt, indeg, outdeg, interaction1 = "globalCom")

# Covar effects
MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "loggedActivity", name="localCom")
MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "daysSinceJoining", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "loggedActivity", name="observation")
MyEffects <- includeEffects(MyEffects,simX, interaction1 = "complexActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "complexActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="localCom")
MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="loggedActivity", name="localCom")
MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="daysSinceJoining", name="localCom")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="loggedActivity", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="localCom")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="observation")
# Effects on behavior
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "complexActivity", name="activityBeh")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "daysSinceJoining", name="activityBeh")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "loggedActivity", name="activityBeh")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "communityActivity", name="activityBeh")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "communityTalkActivity", name="activityBeh")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "localTalkActivity", name="activityBeh")
MyEffects <- includeTimeDummy(MyEffects, density, transTriads, name="localCom", timeDummy = "2")

MyEffects <- includeEffects(MyEffects, avAltEgoX, name = "activityBeh", interaction1="daysSinceJoining", interaction2="localCom")

#MyEffects <- includeEffects(MyEffects,X,name="observation",interaction1="localCom")
MyModel <-sienaModelCreate(projname = "LocalCom8_1.9")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=FALSE)

print(MyResults)
