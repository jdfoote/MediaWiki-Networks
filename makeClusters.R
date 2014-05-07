library(mclust)
library(cluster)
require(Hmisc)

# This script is mostly to record exactly what I'm doing when I create the clusters, and how I'm
# manipulating the data.
# It assumes that the features already exist in R

# Number of clusters for k means/pam
k <- 3
# Number of clusters for mclust
j <- 3
numIterations <- 100
statsColsToInclude <- c(40,41,43:50)
# 

# Calculate mclust
mFit <- Mclust(features, G=j, initialization = list(subset=sample(1:nrow(features), size=1000)))
# Get the best kMeans
kFit <- kmeans(features, k, nstart=numIterations)
kMed <- pam(features, k)

output <- stats[,c('user_id', 'start_date', 'end_date')]
output$kCluster <- kFit$cluster
output$mCluster <- mFit$classification
output$kMedCluster <- kMed$clustering

clusterMeans <- aggregate(stats[,statColsToInclude], by=list(output$kMedCluster), FUN=mean)
clusterMedians <- aggregate(stats[,statsColsToInclude], by=list(output$kMedCluster), FUN=median)


# These provide the basis for the tables, which I cleaned up manually
latex(format.df(clusterMeans, dec=3), file="means.tex", title="Cluster Means")
latex(format.df(clusterMedians, dec=3), file="medians.tex", title="Cluster Medians")

# This calculates the stats for each cluster, which I just added to the table
# number of user-months
print(table(output$kMedCluster))
# number of unique users
print(length(unique(stats[output$kMedCluster == 1,]$user_id)))
print(length(unique(stats[output$kMedCluster == 2,]$user_id)))
print(length(unique(stats[output$kMedCluster == 3,]$user_id)))

write.csv('clusterResults.csv', x=output)
