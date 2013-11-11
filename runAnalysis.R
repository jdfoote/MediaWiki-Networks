if (!"RSiena" %in% installed.packages()) install.packages("RSiena")
if (!"sna" %in% installed.packages()) install.packages("sna")
if (!"network" %in% installed.packages()) install.packages("network")
require(RSiena)
require(sna)
require(network)

net1matrix <- as.matrix(read.table("WeRelateMatrix20120906.csv"))
net2matrix <- as.matrix(read.table("WeRelateMatrix20121013.csv"))
net3matrix <- as.matrix(read.table("WeRelateMatrix20121201.csv"))
allActivity <-as.matrix(read.table("allActivity.dat"))
allActivityPercent <-as.matrix(read.table("allActivitypercentile.dat"))
allPlaces <-as.matrix(read.table("allPlaces.dat"))
allPlacesPercent <-as.matrix(read.table("allPlacespercentile.dat"))
recentActivity <-as.matrix(read.table("recentOverall.dat"))
recentPlaces <-as.matrix(read.table("placeCategories.csv"))
v <- list("allActivity", "allActivityPercent", "allPlaces", "allPlacesPercent", "recentActivity", "recentPlaces")
net1 <- as.network(net1matrix)
net2 <- as.network(net2matrix)
net3 <- as.network(net3matrix)

net1 %v% "recentPlaces1" <- recentPlaces[,1]
net2 %v% "recentPlaces2" <- recentPlaces[,2]
net3 %v% "recentPlaces3" <- recentPlaces[,3]

observation <- sienaNet(array(c(net1matrix, net2matrix, net3matrix),dim=c(342,342,3)))

overallActivity <- varCovar(allActivityPercent)
overallPlaceActivity <- varCovar(allPlacesPercent)
recentAllActivity <- varCovar(recentActivity)
recentPlaceActivity <- sienaNet(recentPlaces, type="behavior")

#MyData <- sienaDataCreate(observation, overallActivity, overallPlaceActivity, recentAllActivity, recentPlaceActivity)
MyData <- sienaDataCreate(observation)

MyEffects <- getEffects(MyData)

MyEffects<- includeEffects(MyEffects, transTrip, cycle3)
MyEffects<-includeEffects(MyEffects,egoX,altX,simX)
#MyEffects<-includeEffects(MyEffects,egoX,altX,simX,interaction1="recentAllActivity")
#MyEffects<-includeEffects(MyEffects,name="recentPlaceActivity",avSim,indeg,outdeg,avAlt,interaction1="observation")
#MyEffects<-includeEffects(MyEffects,name="recentAllActivity",avSim,indeg,outdeg,avAlt,interaction1="observation")

MyModel <-sienaModelCreate(useStdInits = TRUE, projname = "MyResults")
MyResults <- siena07(MyModel, data=MyData, effects=MyEffects,batch=TRUE)

MyResults
