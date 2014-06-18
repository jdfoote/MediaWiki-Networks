library(reshape2)
library(ggplot2)

#clusters.mlt <- melt(clusters, id.vars="id")
#clusters.agg <- aggregate(. ~ id + variable, clusters.mlt, sum)

# The location of the clusters by id file
suffix = '1Trailing'
xAxisText = 'Days since joining'
colors <- c("#d7191c","#fdae61","#2b83ba","#88b083")
xVals <- seq(6,72,6)
xBreaks <- sapply(xVals, function(x) paste('T',x,sep=''))
xLabs <- as.character(xVals*30)
# The minimum number of times a user has to be in a given group in order to
# be shown in the graph for that group
minMonths = 2
#Import the data and add names of clusters
clusterDF <- as.data.frame(read.csv(paste('clustersByID',suffix,'.csv',sep='')))
numCols <- length(clusterDF)
clusterDF[2:numCols][clusterDF[2:numCols]==0] <- 'Low Activity'
clusterDF[2:numCols][clusterDF[2:numCols]==1] <- 'Core Members'
clusterDF[2:numCols][clusterDF[2:numCols]==2] <- 'Peripheral Experts'
clusterDF[2:numCols][clusterDF[2:numCols]==3] <- 'Newbies'

makeGraph <- function(clusters, graphType="fill"){
		ylabel <- if(graphType == 'fill') "Proportion of users in each role" else "Number of users in each role"
		mm <- melt(clusters, id.vars="id", variable.name="Time", value.name="Role")
		plotData <- as.data.frame(with(mm, table(Role, Time)))
		plotData$Role <- factor(plotData$Role, c("Core Members","Peripheral Experts","Newbies","Low Activity"))
		p <- (ggplot(plotData) +
		  geom_area(aes(x=Time, y=Freq, fill=Role, group=Role, order=Role), position=graphType))
		p <- p + scale_fill_manual(values=colors)
		p <- p + scale_x_discrete(breaks=xBreaks,labels=xLabs, name=xAxisText) + ylab(ylabel)
		return(p)
}

makeLineGraph <- function(clusters, includeLA=TRUE){
		mm <- melt(clusters, id.vars="id", variable.name="Time", value.name="Role")
		plotData <- as.data.frame(with(mm, table(Role, Time)))
		plotData$Role <- factor(plotData$Role, c("Core Members","Peripheral Experts","Newbies","Low Activity"))
		if (includeLA == FALSE){
				plotData <- plotData[plotData$Role != 'Low Activity',]
		}
		p <- ggplot(plotData, aes(x=Time, y=Freq, group=Role, color = Role)) + geom_line(alpha=0.5)
		p <- p + scale_color_manual(values=colors)
		p <- p + scale_x_discrete(breaks=xBreaks,labels=xLabs, name=xAxisText) + ylab("Number of users in each role")
		return(p)
}


# Stats for just those who were in each group

ggsave(paste("../Results/allUsers",suffix,"Ratio.pdf",sep=''), plot=makeGraph(clusterDF))
ggsave(paste("../Results/allUsers",suffix,"Line.pdf",sep=''), plot=makeLineGraph(clusterDF))
# A version w/o the Low Activity
ggsave(paste("../Results/allUsers",suffix,"LineNoLowAc.pdf",sep=''), plot=makeLineGraph(clusterDF, FALSE))

cl1 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:numCols] == "Core Members", na.rm=TRUE) >= minMonths}),]
ggsave(paste("../Results/Role1_",minMonths,"+",suffix,".pdf",sep=''), makeGraph(cl1))

cl2 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:numCols] == "Peripheral Experts", na.rm=TRUE) >= minMonths}),]
ggsave(paste("../Results/Role2_",minMonths,"+",suffix,".pdf",sep=''), makeGraph(cl2))

cl3 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:numCols] == "Newbies", na.rm=TRUE) >= minMonths}),]
ggsave(paste("../Results/Role3_",minMonths,"+",suffix,".pdf",sep=''), makeGraph(cl3))

# Calculate the mode for each cluster
Mode <- function(x) {
		# Remove NA
		x <- x[!is.na(x)]
		# Get unique values
		  ux <- unique(x)
		# Figure out which unique value is the max
  ux[which.max(tabulate(match(x, ux)))]
}

modeVals <- apply(clusterDF[,2:numCols], 1, function(x) Mode(x))
modeOut <- as.data.frame(clusterDF[1])
modeOut$mode <- modeVals
save(modeOut, file='modeVals.Rda')

mode0 <- clusterDF[modeVals == "Low Activity",]
ggsave(paste("../Results/Role0Mode",suffix,".pdf",sep=""), makeGraph(mode0))
ggsave(paste("../Results/Role0Mode",suffix,"Stack.pdf",sep=""), makeGraph(mode0,"stack"))
ggsave(paste("../Results/Role0Mode",suffix,"Line.pdf",sep=""), makeLineGraph(mode0))

mode1 <- clusterDF[modeVals == "Core Members",]
ggsave(paste("../Results/Role1Mode",suffix,".pdf",sep=""), makeGraph(mode1))
ggsave(paste("../Results/Role1Mode",suffix,"Stack.pdf",sep=""), makeGraph(mode1,"stack"))
ggsave(paste("../Results/Role1Mode",suffix,"Line.pdf",sep=""), makeLineGraph(mode1))

mode2 <- clusterDF[modeVals == "Peripheral Experts",]
ggsave(paste("../Results/Role2Mode",suffix,".pdf",sep=""), makeGraph(mode2))
ggsave(paste("../Results/Role2Mode",suffix,"Stack.pdf",sep=""), makeGraph(mode2,"stack"))
ggsave(paste("../Results/Role2Mode",suffix,"Line.pdf",sep=""), makeLineGraph(mode2))

mode3 <- clusterDF[modeVals == "Newbies",]
ggsave(paste("../Results/Role3Mode",suffix,".pdf",sep=""), makeGraph(mode3))
ggsave(paste("../Results/Role3Mode",suffix,"Stack.pdf",sep=""), makeGraph(mode3,"stack"))
ggsave(paste("../Results/Role3Mode",suffix,"Line.pdf",sep=""), makeLineGraph(mode3))
