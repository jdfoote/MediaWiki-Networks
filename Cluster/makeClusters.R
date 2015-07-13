library(mclust)
library(cluster)

# This script is mostly to record exactly what I'm doing when I create the clusters, and how I'm
# manipulating the data.
# It assumes that the features already exist in R

# Number of clusters for k means/pam
k <- 3
# Number of clusters for mclust
j <- 3
numIterations <- 100
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

write.csv('clusterResults.csv', x=output)
