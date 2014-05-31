
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
dichotCutoff = 2.9
# Index of first date to include
firstTime = 1
# Index of last date to include
lastTime = 8
numWaves = 8
# Number of nodes
nodeCount = 161

# Load files
filesToImport <- dir("~/Programming/WeRelate/DataFiles/ThesisNetworks", pattern="2*.csv")

importNetwork <- function(fileLocation){
		nFile <- event2dichot(as.matrix(read.table(fileLocation)),method="absolute", thresh=dichotCutoff)
		return(nFile)
}
collab <- array(sapply(filesToImport[seq(1,length(filesToImport),4)], importNetwork), c(nodeCount, nodeCount, numWaves)) 
globCom <- array(sapply(filesToImport[seq(2,length(filesToImport),4)], importNetwork), c(nodeCount, nodeCount, numWaves)) 
locCom <- array(sapply(filesToImport[seq(3,length(filesToImport),4)], importNetwork), c(nodeCount, nodeCount, numWaves)) 
obs <- array(sapply(filesToImport[seq(4,length(filesToImport),4)], importNetwork), c(nodeCount, nodeCount, numWaves))
allNets <- collab + globCom + locCom + obs
allNets[allNets > 1] <- 1

Attributes <- as.data.frame(read.csv('../RSienaAttributeFile2.csv', header = TRUE))
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
		result <- varCovar(matrix(vec, ncol = cols)[,t1:t2])
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
dsj <- cut(Attributes$dayssincefirstedit, 5, labels=FALSE)
daysSinceJoining <- makeVarCovar(dsj)

observation <- sienaNet(obs[,,firstTime:lastTime])
localCom <- sienaNet(locCom[,,firstTime:lastTime])
globalCom <- sienaNet(globCom[,,firstTime:lastTime])
collaboration <- sienaNet(collab[,,firstTime:lastTime])
allInteractions <- sienaNet(totInt[,,firstTime:lastTime])

cluster0 <- sienaNet(clust0[,firstTime:lastTime],type="behavior")
cluster1 <- sienaNet(clust1[,firstTime:lastTime],type="behavior")
cluster2 <- sienaNet(clust2[,firstTime:lastTime],type="behavior")
cluster3 <- sienaNet(clust3[,firstTime:lastTime],type="behavior")
cluster0 <- makeVarCovar(clust0)
cluster2 <- makeVarCovar(clust2)
cluster3 <- makeVarCovar(clust3)

MyData <- sienaDataCreate(observation, cluster0, cluster1, cluster2, cluster3, logged_edits, activeDays, complex_total,local_talk_total, daysSinceJoining)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="clusterTest")

# Include network effects
MyEffects <- includeEffects(MyEffects,transTrip,name="observation")
#MyEffects <- includeEffects(MyEffects,outRate, name="observation",type="rate")
#MyEffects <- includeEffects(MyEffects, transTriads, balance,name="observation")

# Include Behavior effects
MyEffects <- includeEffects(MyEffects,simX, interaction1="cluster1", name="observation","creation")

MyEffects <- includeEffects(MyEffects, name = "cluster1", avAlt, popAlt, interaction1 = "observation")
#MyEffects <- includeEffects(MyEffects, name = "cluster2", avAlt, interaction1 = "observation")
#MyEffects <- includeEffects(MyEffects, name = "cluster0", avAlt, interaction1 = "observation")

# Covar effects
#MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "logged_edits", name="observation")
#MyEffects <- includeEffects(MyEffects,egoX, interaction1 = "daysSinceJoining", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "loggedActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "complex_total", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "complexActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="logged_edits", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="daysSinceJoining", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="loggedActivity", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="observation")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="activityBeh", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "communityTalkActivity", name="observation")
#MyEffects <- includeEffects(MyEffects,simX, interaction1 = "localTalkActivity", name="observation")
# Effects on behavior
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "complexActivity", name="activityBeh")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "daysSinceJoining", name="cluster1")
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "logged_edits", name="cluster1")
#MyEffects <- includeTimeDummy(MyEffects, density, name="observation", timeDummy = "5")

#MyEffects <- includeEffects(MyEffects, avAltEgoX, name = "cluster1", interaction1="daysSinceJoining", interaction2="localCom")

#MyEffects <- includeEffects(MyEffects,X,name="observation",interaction1="localCom")
MyModel <-sienaModelCreate(projname = "observationWithPopAlt")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=FALSE)

siena.table(MyResults, type="latex", file="observationResults.tex", sig=TRUE)
