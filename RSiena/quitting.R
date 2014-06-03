if (!"RSiena" %in% installed.packages()) install.packages("RSiena")
if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
if (!"yaml" %in% installed.packages()) install.packages("yaml")
if (!"igraph" %in% installed.packages()) install.packages("igraph")
require(RSiena)
require(sna)
require(network)
require(yaml)

setwd("~/Programming/WeRelate/DataFiles/ThesisNetworks")

config <- yaml.load_file('~/Programming/WeRelate/Code/config.yaml')

# Determines how to dichotomize. Only values greater than dichotCutoff will be included
# in matrix
dichotCutoff = 1.9
# Index of first date to include
firstTime = 1
# Index of last date to include
lastTime = 4
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
allNets[allNets > 0] <- 1

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

# Calculate centrality and embeddedness, and add as a covariate.
require(igraph)
calcEmbeddedness <- function(netArray){
		# Convert to igraph graphs
		temp <- apply(netArray, MARGIN=3, graph.adjacency)
		# Calculate trans and degree
		trans <- sapply(temp, transitivity, type="local", isolates="zero")
		deg <- sapply(temp, degree)
		# Multiply transitivity and degree
		return(trans*deg)
}


# MAKE SURE TO CHANGE THE NETWORK THIS APPLIES TO
eigenvectorCentrality <- makeVarCovar(apply(allNets,MARGIN=3,FUN=sna::evcent))
embeddedness <- makeVarCovar(calcEmbeddedness(allNets))

# Create dependent variables
observation <- sienaNet(obs[,,firstTime:lastTime])
observation <- sienaNet(locCom[,,firstTime:lastTime])
globalCom <- sienaNet(globCom[,,firstTime:lastTime])
collaboration <- sienaNet(collab[,,firstTime:lastTime])
allInteractions <- sienaNet(allNets[,,firstTime:lastTime])

cluster0 <- sienaNet(clust0[,firstTime:lastTime],type="behavior")
cluster1 <- sienaNet(clust1[,firstTime:lastTime],type="behavior")
cluster2 <- sienaNet(clust2[,firstTime:lastTime],type="behavior")
cluster3 <- sienaNet(clust3[,firstTime:lastTime],type="behavior")
#cluster0 <- makeVarCovar(clust0)
cluster1 <- makeVarCovar(clust1)
cluster2 <- makeVarCovar(clust2)
cluster3 <- makeVarCovar(clust3)

MyData <- sienaDataCreate(allInteractions, cluster0, cluster1, cluster2, cluster3, logged_edits, activeDays, complex_total,local_talk_total, daysSinceJoining, eigenvectorCentrality, embeddedness)

MyEffects <- getEffects(MyData)

print01Report(MyData, MyEffects, modelname="quittingAnalysis")

# Include network effects
#MyEffects <- includeEffects(MyEffects,transTrip,name="allInteractions")
#MyEffects <- includeEffects(MyEffects,outRate, name="allInteractions",type="rate")
MyEffects <- includeEffects(MyEffects, transTrip, balance,name="allInteractions")

# Include Behavior effects
#MyEffects <- includeEffects(MyEffects,simX, interaction1="cluster0", name="allInteractions")
#MyEffects <- includeEffects(MyEffects, name = "cluster0", avAlt, interaction1 = "allInteractions")

# Covar effects
#MyEffects <- includeEffects(MyEffects,egoX,simX, interaction1 = "complex_total", name="allInteractions")
#MyEffects <- includeEffects(MyEffects, RateX, type="rate", interaction1="logged_edits", name="allInteractions")

# Effects on behavior
#MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "daysSinceJoining", name="cluster1")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "eigenvectorCentrality", name="cluster0")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "embeddedness", name="cluster0")
MyEffects <- includeEffects(MyEffects,effFrom, interaction1 = "cluster1", name="cluster0")
#MyEffects <- includeTimeDummy(MyEffects, density, name="allInteractions", timeDummy = "4,5")

#MyEffects <- includeEffects(MyEffects, avAltEgoX, name = "cluster1", interaction1="daysSinceJoining", interaction2="allInteractions")

#MyEffects <- includeEffects(MyEffects,X,name="allInteractions",interaction1="allInteractions")
MyModel <-sienaModelCreate(projname = "allInteractionsQuitting")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=FALSE,returnDeps=TRUE)

siena.table(MyResults, type="latex", file="allInteractionsQuittingResults.tex", sig=TRUE)
