if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
if (!"yaml" %in% installed.packages()) install.packages("yaml")
if (!"igraph" %in% installed.packages()) install.packages("igraph")
#require(RSiena)
require(sna)
require(network)
require(yaml)
require(Hmisc)
require(igraph)
require(stargazer)

config <- yaml.load_file('~/Programming/WeRelate/Code/config.yaml')
attributes <- as.data.frame(read.csv('~/Programming/WeRelate/DataFiles/RSienaAttributeFile2.csv'))

# Determines how to dichotomize. Only values greater than dichotCutoff will be included
# in matrix
dichotCutoff = 1.9
# Index of first date to include
firstTime = 1
# Index of last date to include
lastTime = 8
numWaves = 8
# Number of nodes
nodeCount = 161

setwd("~/Programming/WeRelate/DataFiles/ThesisNetworks")

filesToImport <- dir("~/Programming/WeRelate/DataFiles/ThesisNetworks/", pattern="2*.csv")

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

fullObs <- apply(obs,MARGIN=1:2,FUN=sum)
fullObs[fullObs > 1] <- 1
fullLocal <- apply(locCom,MARGIN=1:2,FUN=sum)
fullLocal[fullLocal > 1] <- 1
fullGlobal <- apply(globCom,MARGIN=1:2,FUN=sum)
fullGlobal[fullGlobal > 1] <- 1
fullCollab <- apply(collab,MARGIN=1:2,FUN=sum)
fullCollab[fullCollab > 1] <- 1

# Get the modes for each of the users in this dataset
load("../modeVals.Rda")
Attributes <- as.data.frame(read.csv('../RSienaAttributeFile2.csv', header = TRUE))
netStats <- subset(modeOut, id %in% Attributes$user_id)

# Create a color vector, based on role
netStats$color[netStats$mode=='Low Activity'] <- "gray"
netStats$color[netStats$mode=='Central Members'] <- "lightblue"
netStats$color[netStats$mode=='Peripheral Experts'] <- "lightgreen"
netStats$color[netStats$mode=='Newbies'] <- "orange"

# Calculate centrality, degree, and clustering coefficient and add to features

# Create igraph objects.
obsIgraph = graph.adjacency(fullObs)
lcIgraph = graph.adjacency(fullLocal)
gcIgraph = graph.adjacency(fullGlobal)
cIgraph = graph.adjacency(fullCollab)

netStats$obsDeg <- degree(obsIgraph)
netStats$lcDeg <- degree(lcIgraph)
netStats$gcDeg <- degree(gcIgraph)
netStats$cDeg <- degree(cIgraph)

netStats$obsEigCent <- evcent(obsIgraph)$vector
netStats$lcEigCent <- evcent(lcIgraph)$vector
netStats$gcEigCent <- evcent(gcIgraph)$vector
netStats$cEigCent <- evcent(cIgraph)$vector


netStats$obsClus <- transitivity(obsIgraph, type="local", isolates="zero")
netStats$lcClus <- transitivity(lcIgraph, type="local", isolates="zero")
netStats$gcClus <- transitivity(gcIgraph, type="local", isolates="zero")
netStats$cClus <- transitivity(cIgraph, type="local", isolates="zero")

clusterMeans <- aggregate(netStats[,4:15], by=list(netStats$mode), FUN=mean)
clusterMedians <- aggregate(netStats[,4:15], by=list(netStats$mode), FUN=median)

meanData <- as.data.frame(t(clusterMeans[,2:13]))
names(meanData) <- clusterMeans$Group.1
medianData <- as.data.frame(t(clusterMedians[,2:13]))
names(medianData) <- clusterMedians$Group.1
# These provide the basis for the tables, which I cleaned up manually
latex(format.df(meanData, dec=3), file="networkMeans.tex", title="Cluster Network Means")
latex(format.df(medianData, dec=3), file="networkMedians.tex", title="Cluster Network Medians")

# Number of users in each role, to be added to tables
print(table(netStats$mode))

# Community detection

makeCommunityPlot <-function(g, fname){
		# Get color from netstats
		V(g)$color <- netStats$color
		V(g)$id <- netStats$id
		# Delete isolates
		g <- delete.vertices(g, which(degree(g) < 1))
		# Size by eigenvector centrality
		V(g)$size <- (evcent(g)$vector +.3)*11
		# Create community vector
		communityPartitions <- walktrap.community(g)
		# Select where to save
		pdf(fname)
		l <- layout.fruchterman.reingold(g,niter=500,area=vcount(g)^2.3,repulserad=vcount(g)^2.8)
		pl <-plot(communityPartitions, g,
				  layout=l,
				  vertex.label = V(g)$id,
				  vertex.label.cex=.3,
				  vertex.color <- g$color,
				  edge.arrow.size=.3,
				  edge.color='black')
		dev.off()
}

makeCommunityPlot(obsIgraph, 'observationComPlot.pdf')
makeCommunityPlot(lcIgraph, 'localComPlot.pdf')
makeCommunityPlot(gcIgraph, 'globalComPlot.pdf')
makeCommunityPlot(cIgraph, 'collabPlot.pdf')

# Figure out the percentage of users in role who are all in the same cluster - this is ugly, but don't have time to clean up right now
ratioInTopCluster <- function(g, role){
		comm <- walktrap.community(g)$membership
		totRole <- sum(netStats$mode==role)
		topClustRatio <- sort(table(comm[netStats$mode==role]), decreasing=TRUE[1])[1]/totRole
		return(topClustRatio)
}

ratiosCluster <- sapply(list(obsIgraph,lcIgraph,gcIgraph,cIgraph), function(x) sapply(c('Central Members', 'Low Activity', 'Newbies', 'Peripheral Experts'), function(y) ratioInTopCluster(x,y)))

colnames(ratiosCluster) <- c('Observation', 'Local Talk', 'Global Talk', 'Collaboration')
stargazer(ratiosCluster)
