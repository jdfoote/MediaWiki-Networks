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

o0 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_06_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o1 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_07_03_observation.csv")),method="absolute", thresh=dichotCutoff)
o2 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_08_02_observation.csv")),method="absolute", thresh=dichotCutoff)
o3 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_09_01_observation.csv")),method="absolute", thresh=dichotCutoff)
o4 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_01_observation.csv")),method="absolute", thresh=dichotCutoff)
o5 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_31_observation.csv")),method="absolute", thresh=dichotCutoff)
o6 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_11_30_observation.csv")),method="absolute", thresh=dichotCutoff)
o7 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_12_30_observation.csv")),method="absolute", thresh=dichotCutoff)
lc0 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_06_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc1 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_07_03_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc2 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_08_02_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc3 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_09_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc4 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_01_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc5 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_31_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc6 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_11_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
lc7 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_12_30_localComm.csv")),method="absolute", thresh=dichotCutoff)
gc0 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_06_03_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc1 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_07_03_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc2 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_08_02_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc3 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_09_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc4 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_01_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc5 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_31_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc6 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_11_30_globalComm.csv")),method="absolute", thresh=dichotCutoff)
gc7 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_12_30_globalComm.csv")),method="absolute", thresh=dichotCutoff)
c0 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_06_03_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c1 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_07_03_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c2 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_08_02_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c3 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_09_01_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c4 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_01_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c5 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_10_31_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c6 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_11_30_collaboration.csv")),method="absolute", thresh=dichotCutoff)
c7 <- event2dichot(as.matrix(read.table("ThesisNetworks/2012_12_30_collaboration.csv")),method="absolute", thresh=dichotCutoff)

# Create the combined networks

fullObs <- event2dichot(o0 + o1 + o2 + o3 + o4 + o5 + o6 + o7, method="absolute", thresh=0.9)
fullLocal <- event2dichot(lc0 + lc1 + lc2 + lc3 + lc4 + lc5 + lc6 + lc7, method="absolute", thresh=0.9)
fullGlobal <- event2dichot(gc0 + gc1 + gc2 + gc3 + gc4 + gc5 + gc6 + gc7, method="absolute", thresh=0.9)
fullCollab <- event2dichot(c0 + c1 + c2 + c3 + c4 + c5 + c6 + c7, method="absolute", thresh=0.9)

# Get the modes for each of the users in this dataset
load("modeVals.Rda")
netStats <- subset(modeOut, id %in% attributes$user_id)
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
		V(g)$size <- evcent(g)$vector*15
		# Create community vector
		communityPartitions <- walktrap.community(g)
		# Select where to save
		pdf(fname)
		l <- layout.fruchterman.reingold(g,niter=500,area=vcount(g)^2.3,repulserad=vcount(g)^2.8)
		l <- layout.fruchterman.reingold(g)
		pl <-plot(communityPartitions, g,
				  layout=layout.fruchterman.reingold,
				  vertex.label = V(g)$id,
				  vertex.label.cex=1,
				  vertex.color <- V(g)$color,
				  edge.arrow.size=.3)
		dev.off()
}

makeCommunityPlot(lcIgraph, 'localComPlot.pdf')
makeCommunityPlot(gcIgraph, 'globalComPlot.pdf')
makeCommunityPlot(cIgraph, 'collabPlot.pdf')

