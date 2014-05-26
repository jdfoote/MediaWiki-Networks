if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
if (!"yaml" %in% installed.packages()) install.packages("yaml")
if (!"igraph" %in% installed.packages()) install.packages("igraph")
#require(RSiena)
require(sna)
require(network)
require(yaml)
require(igraph)

config <- yaml.load_file('~/Programming/WeRelate/Code/config.yaml')
attributes <- as.data.frame(read.csv('~/Programming/WeRelate/DataFiles/RSienaAttributeFile.csv'))

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

# Calculate centrality, degree, and clustering coefficient and add to features

# Create igraph objects.
obsIgraph = graph.adjacency(fullObs)
lcIgraph = graph.adjacency(fullLocal)
gcIgraph = graph.adjacency(fullGlobal)
cIgraph = graph.adjacency(fullCollab)

attributes$obsDeg <- degree(obsIgraph)
attributes$lcDeg <- degree(lcIgraph)
attributes$gcDeg <- degree(gcIgraph)
attributes$cDeg <- degree(cIgraph)

attributes$obsEigCent <- evcent(obsIgraph)
attributes$lcEigCent <- evcent(lcIgraph)
attributes$gcEigCent <- evcent(gcIgraph)
attributes$cEigCent <- evcent(cIgraph)

attributes$obsClus <- transitivity(obsIgraph, type="local", isolates="zero")
attributes$lcClus <- transitivity(lcIgraph, type="local", isolates="zero")
attributes$gcClus <- transitivity(gcIgraph, type="local", isolates="zero")
attributes$cClus <- transitivity(cIgraph, type="local", isolates="zero")


# Community detection

# Start by removing isolates
obsIgraph <- delete.vertices(obsIgraph, which(degree(obsIgraph) < 1))
lcIgraph <- delete.vertices(lcIgraph, which(degree(lcIgraph) < 1))
obsComms <- walktrap.community(obsIgraph)
lcComms <- walktrap.community(lcIgraph)
gcComms <- walktrap.community(gcIgraph)
cComms <- walktrap.community(cIgraph)

plot(lcComms, lcIgraph,
	 layout=layout.fruchterman.reingold)
