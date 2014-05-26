library(reshape2)
library(ggplot2)

#clusters.mlt <- melt(clusters, id.vars="id")
#clusters.agg <- aggregate(. ~ id + variable, clusters.mlt, sum)

# The location of the clusters by id file
trailingZeroes = 1
# The minimum number of times a user has to be in a given group in order to
# be shown in the graph for that group
minMonths = 2

#Import the data and add names of clusters
clusterDF <- as.data.frame(read.csv(paste('clustersByID',trailingZeroes,'Trailing.csv',sep='')))
clusterDF[2:76][clusterDF[2:76]==0] <- 'Low Activity'
clusterDF[2:76][clusterDF[2:76]==1] <- 'Central Members'
clusterDF[2:76][clusterDF[2:76]==2] <- 'Peripheral Experts'
clusterDF[2:76][clusterDF[2:76]==3] <- 'Newbies'

makeGraph <- function(clusters, graphType="fill"){
		ylabel <- if(graphType == 'fill') "Proportion of users in each cluster" else "Number of users in each cluster"
		mm <- melt(clusters, id.vars="id", variable.name="Time", value.name="Role")
		plotData <- as.data.frame(with(mm, table(Role, Time)))
		plotData$Role <- factor(plotData$Role, c("Central Members","Peripheral Experts","Newbies","Low Activity"))
		p <- (ggplot(plotData) +
		  geom_area(aes(x=Time, y=Freq, fill=Role, group=Role, order=Role), position=graphType))
		p <- p + scale_fill_manual(values=c("#69D2E7","#A7DBD8","#E0E4CC","#F38630"))
		p <- p + scale_x_discrete(breaks=NULL, name="Time since joining") + ylab(ylabel)
		return(p)
}

makeLineGraph <- function(clusters, includeLA=TRUE){
		mm <- melt(clusters, id.vars="id", variable.name="Time", value.name="Role")
		plotData <- as.data.frame(with(mm, table(Role, Time)))
		plotData$Role <- factor(plotData$Role, c("Central Members","Peripheral Experts","Newbies","Low Activity"))
		if (includeLA == FALSE){
				plotData <- plotData[plotData$Role != 'Low Activity',]
		}
		p <- ggplot(plotData, aes(x=Time, y=Freq, group=Role, color = Role)) + geom_line(alpha=0.5)
		p <- p + scale_color_manual(values=c("#69D2E7","#A7DBD8","#E0E4CC","#F38630"))
		p <- p + scale_x_discrete(breaks=NULL, name="Time since joining") + ylab("Number of users in each cluster")
		return(p)
}

#print(ggplot(clusters.mlt) +
 # stat_summary(aes(x=variable, y=value, fill=id, group=id), fun.y=sum, position="fill", geom="area"))

# Stats for just those who were in each group

ggsave(file="../Results/allUsersRatio.pdf", plot=makeGraph(clusterDF))
ggsave(file="../Results/allUsersLine.pdf", plot=makeLineGraph(clusterDF))
# A version w/o the Low Activity
ggsave(file="../Results/allUsersLineNoLowAc.pdf", plot=makeLineGraph(clusterDF, FALSE))

cl1 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "Central Members", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role1_2+.pdf", makeGraph(cl1))

cl2 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "Peripheral Experts", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role2_2+.pdf", makeGraph(cl2))

cl3 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "Newbies", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role3_2+.pdf", makeGraph(cl3))

# Calculate a version for each of the modal clusters
Mode <- function(x) {
		x <- x[!is.na(x)]
		  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

modeVals <- apply(clusterDF[,2:76], 1, function(x) Mode(x))
modeOut <- as.data.frame(clusterDF[1])
modeOut$mode <- modeVals
save(modeOut, file='modeVals.Rda')

mode0 <- clusterDF[modeVals == "Low Activity",]
ggsave(paste("../Results/Role0Mode",trailingZeroes,"Trailing.pdf",sep=""), makeGraph(mode0))
ggsave(paste("../Results/Role0Mode",trailingZeroes,"TrailingStack.pdf",sep=""), makeGraph(mode0,"stack"))
ggsave(paste("../Results/Role0Mode",trailingZeroes,"TrailingLine.pdf",sep=""), makeLineGraph(mode0))

mode1 <- clusterDF[modeVals == "Central Members",]
ggsave(paste("../Results/Role1Mode",trailingZeroes,"Trailing.pdf",sep=""), makeGraph(mode1))
ggsave(paste("../Results/Role1Mode",trailingZeroes,"TrailingStack.pdf",sep=""), makeGraph(mode1,"stack"))
ggsave(paste("../Results/Role1Mode",trailingZeroes,"TrailingLine.pdf",sep=""), makeLineGraph(mode1))

mode2 <- clusterDF[modeVals == "Peripheral Experts",]
ggsave(paste("../Results/Role2Mode",trailingZeroes,"Trailing.pdf",sep=""), makeGraph(mode2))
ggsave(paste("../Results/Role2Mode",trailingZeroes,"TrailingStack.pdf",sep=""), makeGraph(mode2,"stack"))
ggsave(paste("../Results/Role2Mode",trailingZeroes,"TrailingLine.pdf",sep=""), makeLineGraph(mode2))

mode3 <- clusterDF[modeVals == "Newbies",]
ggsave(paste("../Results/Role3Mode",trailingZeroes,"Trailing.pdf",sep=""), makeGraph(mode3))
ggsave(paste("../Results/Role3Mode",trailingZeroes,"TrailingStack.pdf",sep=""), makeGraph(mode3,"stack"))
ggsave(paste("../Results/Role3Mode",trailingZeroes,"TrailingLine.pdf",sep=""), makeLineGraph(mode3))
