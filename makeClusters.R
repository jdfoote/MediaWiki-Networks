library(mclust)

# This script is mostly to record exactly what I'm doing when I create the clusters, and how I'm
# manipulating the data.
# Number of clusters for k means
k <- 5
# Number of clusters for mclust
j <- 5
numIterations <- 100

# 

# Calculate mclust
mFit <- Mclust(features, G=j, initialization = list(subset=sample(1:nrow(features), size=1000)))
# Get the best kMeans
kFit <- kmeans(features, k, nstart=numIterations)

output <- stats[,c('user_id', 'start_date', 'end_date')]
output$kClusters <- kFit$cluster
output$mClusters <- mFit$classification

write.csv('clusterResults.csv', x=output)

