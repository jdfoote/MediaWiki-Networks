
if (!"RSiena" %in% installed.packages()) install.packages("RSiena")
if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
if (!"yaml" %in% installed.packages()) install.packages("yaml")
require(RSiena)
require(sna)
require(network)
require(yaml)

config <- yaml.load_file('~/Programming/WeRelate/Code/config.yaml')

# Determines how to dichotomize. Only values greater than dichotCutoff will be included
# in matrix
dichotCutoff = 1.9
# Index of first date to include
firstTime = 2
# Index of last date to include
lastTime = 8
numWaves = 8
# Number of nodes
nodeCount = 267

o0 <- event2dichot(as.matrix(read.table("2012_06_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o1 <- event2dichot(as.matrix(read.table("2012_07_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o2 <- event2dichot(as.matrix(read.table("2012_08_02_observation.csv")),method="absolute", thresh=dichotCutoff)
o3 <- event2dichot(as.matrix(read.table("2012_09_01_observation.csv")),method="absolute", thresh=dichotCutoff)
o4 <- event2dichot(as.matrix(read.table("2012_10_01_observation.csv")),method="absolute", thresh=dichotCutoff)
o5 <- event2dichot(as.matrix(read.table("2012_10_31_observation.csv")),method="absolute", thresh=dichotCutoff)
o6 <- event2dichot(as.matrix(read.table("2012_11_30_observation.csv")),method="absolute", thresh=dichotCutoff)
o7 <- event2dichot(as.matrix(read.table("2012_12_30_observation.csv")),method="absolute", thresh=dichotCutoff)
lc0 <- event2dichot(as.matrix(read.table("2012_06_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc1 <- event2dichot(as.matrix(read.table("2012_07_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc2 <- event2dichot(as.matrix(read.table("2012_08_02_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc3 <- event2dichot(as.matrix(read.table("2012_09_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc4 <- event2dichot(as.matrix(read.table("2012_10_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc5 <- event2dichot(as.matrix(read.table("2012_10_31_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc6 <- event2dichot(as.matrix(read.table("2012_11_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc7 <- event2dichot(as.matrix(read.table("2012_12_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
gc0 <- event2dichot(as.matrix(read.table("2012_06_03_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc1 <- event2dichot(as.matrix(read.table("2012_07_03_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc2 <- event2dichot(as.matrix(read.table("2012_08_02_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc3 <- event2dichot(as.matrix(read.table("2012_09_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc4 <- event2dichot(as.matrix(read.table("2012_10_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc5 <- event2dichot(as.matrix(read.table("2012_10_31_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc6 <- event2dichot(as.matrix(read.table("2012_11_30_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc7 <- event2dichot(as.matrix(read.table("2012_12_30_globalComm.csv")),method="absolute", thresh=dichotCutoff)
c0 <- event2dichot(as.matrix(read.table("2012_06_03_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c1 <- event2dichot(as.matrix(read.table("2012_07_03_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c2 <- event2dichot(as.matrix(read.table("2012_08_02_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c3 <- event2dichot(as.matrix(read.table("2012_09_01_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c4 <- event2dichot(as.matrix(read.table("2012_10_01_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c5 <- event2dichot(as.matrix(read.table("2012_10_31_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c6 <- event2dichot(as.matrix(read.table("2012_11_30_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c7 <- event2dichot(as.matrix(read.table("2012_12_30_collaboration.csv")),method="absolute", thresh=dichotCutoff)
obs <- array(c(c0,c1,c2,c3,c4,c5,c6,c7),c(nodeCount, nodeCount, numWaves))
locCom <- array(c(lc0,lc1,lc2,lc3,lc4,lc5,lc6,lc7),c(nodeCount, nodeCount, numWaves))
globCom <- array(c(gc0,gc1,gc2,gc3,gc4,gc5,gc6,gc7),c(nodeCount, nodeCount, numWaves))
collab <- array(c(c0,c1,c2,c3,c4,c5,c6,c7),c(nodeCount, nodeCount, numWaves))


Attributes <- as.data.frame(read.csv('../RSienaAttributeFile.csv', header = TRUE))
# Sort by date, then userID
Attributes <- Attributes[with(Attributes, order(start_date, user_id)),]
# Create dummy variables for clusters
clusters <- model.matrix(~factor(Attributes$kMedCluster)-1)
clust0 <- matrix(clusters[,1],ncol=8)
clust1 <- matrix(clusters[,2],ncol=8)
clust2 <- matrix(clusters[,3],ncol=8)
clust3 <- matrix(clusters[,4],ncol=8)

# Function to create covariates from vectors
makeVarCovar <- function(vec,cols = 8, t1 = firstTime, t2 = lastTime){
		result <- varCovar(matrix(vec, ncol = cols)[,firstTime:lastTime])
		return(result)
}

# Create summary covars
simple_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$simple_edits)]))
community_talk_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$community_talk_edits)]))
community_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$community_edits)]))
complex_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$complex_edits)]))
other_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$other_edits)]))
local_talk_total <- makeVarCovar(rowSums(Attributes[,c(config$editCats$local_talk_edits)]))
logged_edits <- makeVarCovar(log(Attributes$all_edits+1))
logged_manual_edits <- makeVarCovar(log(Attributes$manual_edits + 1))

# Create attribute vars
activeDays <- makeVarCovar(Attributes$active_days)
# Change activeDays into ordinal
activePeriods <- cut(activeDays, c(-1,0,5,10,20,30), labels=FALSE)
daysSinceJoining <- makeVarCovar(Attributes$dayssincefirstedit)

observation <- sienaNet(obs[,,firstTime:lastTime])
localCom <- sienaNet(locCom[,,firstTime:lastTime])
globalCom <- sienaNet(globCom[,,firstTime:lastTime])
collaboration <- sienaNet(collab[,,firstTime:lastTime])

cluster0 <- sienaNet(clust0[,firstTime:lastTime],type="behavior")
cluster1 <- sienaNet(clust1[,firstTime:lastTime],type="behavior")
cluster2 <- sienaNet(clust2[,firstTime:lastTime],type="behavior")
cluster3 <- sienaNet(clust3[,firstTime:lastTime],type="behavior")

MyData <- sienaDataCreate(localCom, cluster0, cluster1, cluster2, cluster3, logged_edits, activeDays, complex_total,local_talk_total)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="clusterTest")

# Include network effects
#MyEffects <- includeEffects(MyEffects,transTrip,cycle3,outRate,name="observation")
#MyEffects <- includeEffects(MyEffects,outRate, name="observation",type="rate")
MyEffects <- includeEffects(MyEffects, transTriads, balance,name="localCom")

# Include Behavior effects
#MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="activityBeh", name="observation")
MyEffects <- includeEffects(MyEffects,egoX,altX,simX, interaction1="cluster1", name="localCom")

#MyEffects <- includeEffects(MyEffects, name = "activityBeh", avAlt, indeg, outdeg, interaction1 = "observation")
MyEffects <- includeEffects(MyEffects, name = "cluster1", avAlt, interaction1 = "localCom")
#MyEffects <- includeEffects(MyEffects, name = "activityBeh", avAlt, indeg, outdeg, interaction1 = "globalCom")

# Covar effects
MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "logged_edits", name="localCom")
MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "daysSinceJoining", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "loggedActivity", name="observation")
MyEffects <- includeEffects(MyEffects,simX, interaction1 = "complex_total", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "complexActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="localCom")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="localCom")
MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="logged_edits", name="localCom")
MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="daysSinceJoining", name="localCom")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="loggedActivity", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="localCom")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="observation")
# Effects on behavior
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "complexActivity", name="activityBeh")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "daysSinceJoining", name="cluster1")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "logged_edits", name="cluster1")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "communityActivity", name="cluster1")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "communityTalkActivity", name="activityBeh")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "localTalkActivity", name="activityBeh")
#MyEffects <- includeTimeDummy(MyEffects, density, transTriads, name="localCom", timeDummy = "2")

MyEffects <- includeEffects(MyEffects, avAltEgoX, name = "cluster1", interaction1="daysSinceJoining", interaction2="localCom")

#MyEffects <- includeEffects(MyEffects,X,name="observation",interaction1="localCom")
MyModel <-sienaModelCreate(projname = "LocalCom_firstTest")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=FALSE)

print(MyResults)
