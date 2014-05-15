library(reshape2)
library(ggplot2)

#clusters.mlt <- melt(clusters, id.vars="id")
#clusters.agg <- aggregate(. ~ id + variable, clusters.mlt, sum)

# The location of the clusters by id file
trailingZeroes = 1
clusterDF <- as.data.frame(read.csv(paste('clustersByID',trailingZeroes,'Trailing.csv',sep='')))
# The minimum number of times a user has to be in a given group in order to
# be shown in the graph for that group
minMonths = 2

makeGraph <- function(clusters, graphType="fill"){
		ylabel <- if(graphType == 'fill') "Proportion of users in each cluster" else "Number of users in each cluster"
		clus1 <- apply(clusters, 2, function(x) {sum(x=='1', na.rm=TRUE)})
		clus2 <- apply(clusters, 2, function(x) {sum(x=='2', na.rm=TRUE)})
		clus3 <- apply(clusters, 2, function(x) {sum(x=='3', na.rm=TRUE)})
		clus0 <- apply(clusters, 2, function(x) {sum(x=='0', na.rm=TRUE)})
		clusters2 <- data.frame(clus0, clus1, clus2, clus3)
		c2 <- t(clusters2)
		c3 <- as.data.frame(c2)
		c3$id = c('Low Activity Cluster', 'Central Members', 'Peripheral Experts', 'Newbies')
		c3 <- c3[order(c(1,4,3,2)),]
		print(c3)
		p <- (ggplot(melt(c3, id.vars="id")) +
		  geom_area(aes(x=variable, y=value, fill=id, group=id), position=graphType))
		p <- p + scale_fill_manual(values=c("#69D2E7","#A7DBD8","#E0E4CC","#F38630"))
		p <- p + scale_x_discrete(breaks=NULL, name="Time since joining") + ylab("Proportion of users in each cluster")
		return(p)
}

makeLineGraph <- function(clusters){
		clus1 <- apply(clusters, 2, function(x) {sum(x=='1', na.rm=TRUE)})
		clus2 <- apply(clusters, 2, function(x) {sum(x=='2', na.rm=TRUE)})
		clus3 <- apply(clusters, 2, function(x) {sum(x=='3', na.rm=TRUE)})
		clus0 <- apply(clusters, 2, function(x) {sum(x=='0', na.rm=TRUE)})
		clusters2 <- data.frame(clus0, clus1, clus2, clus3)
		c2 <- t(clusters2)
		c3 <- as.data.frame(c2)
		c3$id = c('Low Activity Cluster', 'Central Members', 'Peripheral Experts', 'Newbies')
		c3 <- c3[order(c(1,4,3,2)),]
		p <- ggplot(melt(c3, id.vars="id"), aes(x=variable, y=value, group=id, color = id)) + geom_path(alpha=0.5)
		p <- p + scale_fill_manual(values=c("#69D2E7","#A7DBD8","#E0E4CC","#F38630"))
		p <- p + scale_x_discrete(breaks=NULL, name="Time since joining") + ylab("Number of users in each cluster")
		return(p)
}

#print(ggplot(clusters.mlt) +
 # stat_summary(aes(x=variable, y=value, fill=id, group=id), fun.y=sum, position="fill", geom="area"))

# Stats for just those who were in each group

ggsave(file="../Results/allUsers.png", plot=makeGraph(clusterDF))

cl1 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "1", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role1_2+.png", makeGraph(cl1))

cl2 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "2", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role2_2+.png", makeGraph(cl2))

cl3 <- clusterDF[apply(clusterDF, 1, function(x) {sum(x[2:76] == "3", na.rm=TRUE) >= minMonths}),]
ggsave("../Results/Role3_2+.png", makeGraph(cl3))

# Calculate a version for each of the modal clusters
Mode <- function(x) {
		x <- x[!is.na(x)]
		  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

modeVals <- apply(clusterDF[,2:76], 1, function(x) Mode(x))

mode0 <- clusterDF[modeVals == 0,]
ggsave(paste("../Results/Role0Mode",trailingZeroes,"Trailing.png",sep=""), makeGraph(mode0))
ggsave(paste("../Results/Role0Mode",trailingZeroes,"TrailingStack.png",sep=""), makeGraph(mode0,"stack"))
ggsave(paste("../Results/Role0Mode",trailingZeroes,"TrailingLine.png",sep=""), makeLineGraph(mode0))

mode1 <- clusterDF[modeVals == 1,]
ggsave(paste("../Results/Role1Mode",trailingZeroes,"Trailing.png",sep=""), makeGraph(mode1))
ggsave(paste("../Results/Role1Mode",trailingZeroes,"TrailingStack.png",sep=""), makeGraph(mode1,"stack"))
ggsave(paste("../Results/Role1Mode",trailingZeroes,"TrailingLine.png",sep=""), makeLineGraph(mode1))

mode2 <- clusterDF[modeVals == 2,]
ggsave(paste("../Results/Role2Mode",trailingZeroes,"Trailing.png",sep=""), makeGraph(mode2))
ggsave(paste("../Results/Role2Mode",trailingZeroes,"TrailingStack.png",sep=""), makeGraph(mode2,"stack"))
ggsave(paste("../Results/Role2Mode",trailingZeroes,"TrailingLine.png",sep=""), makeLineGraph(mode2))

mode3 <- clusterDF[modeVals == 3,]
ggsave(paste("../Results/Role3Mode",trailingZeroes,"Trailing.png",sep=""), makeGraph(mode3))
ggsave(paste("../Results/Role3Mode",trailingZeroes,"TrailingStack.png",sep=""), makeGraph(mode3,"stack"))
ggsave(paste("../Results/Role3Mode",trailingZeroes,"TrailingLine.png",sep=""), makeLineGraph(mode3))
