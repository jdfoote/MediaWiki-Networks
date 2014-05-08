library(yaml)
library(mclust)
library(NbClust)

# This script takes a statsRatios file, combines the stats into some broader categories, then applies both kMeans and mclust (GMM) clustering algorithms, for k = 1:kMax. It saves 2 PNG files showing the
# withinss for kmeans, and the BIC for mclust.
kMax <- 10
numIterations <- 100
config <- yaml.load_file('../Code/config.yaml')

stats <- read.csv('../DataFiles/userStatsRatios.csv', header = T)

stats$simple_total <- rowSums(stats[,c(config$editCats$simple_edits)])
stats$community_talk_total <- rowSums(stats[,c(config$editCats$community_talk_edits)])
stats$community_total <- rowSums(stats[,c(config$editCats$community_edits)])
stats$complex_total <- rowSums(stats[,c(config$editCats$complex_edits)])
stats$other_total <- rowSums(stats[,c(config$editCats$other_edits)])
stats$local_talk_total <- rowSums(stats[,c(config$editCats$local_talk_edits)])
stats$logged_edits <- log(stats$all_edits+1)
stats$logged_manual_edits <- log(stats$manual_edits + 1)

# Create a variable that holds the features we want to use for clustering
features <- stats[,c("logged_edits", "logged_manual_edits", "active_days", "simple_total", "complex_total", "community_total", "other_total", "local_talk_total", "community_talk_total")]
features <- scale(features)

#nbCl <- NbClust(features)

# Code to do clustering
# Make graphs to find best clustering
makeGraphs <- function(x, kMax, numIterations){
	# Initialize results matrix
	kResult <- vector()
	mResult <- vector()
	# For each k value
	for (j in 1:kMax) {
		print(paste("Calculating k: ", j))
		# Calculate mclust stuff
		mResult[j] <- Mclust(x, G=j, initialization = list(subset=sample(1:nrow(x), size=1000)))$bic
		# Get the best k means withinss
		kResult[j] <- findBestKMeans(x, j, numIterations)$tot.withinss
	}

	#Plot kmeans results
	png(filename="./kMeans.png", height=500, width=500, bg="white")
	plot(kResult, type="o", col="blue", ylim=c(0,max(kResult)), main="KMeans Within SS by k value", xlab="K Values", ylab="Within-cluster sum of squares")
	box()
	legend(8, max(kResult), c("Behavioral Roles"), col=c("blue"),lty=1)
	dev.off()

	# Plot Mclust results
	png(filename="./mclust.png", height=500, width=500, bg="white")
	plot(mResult, type="o", col="blue", ylim=c(min(mResult),0), main="GMM BIC by k value", xlab="K Values", ylab="BIC")
	box()
	legend(1, max(mResult), c("Behavioral Roles"), col=c("blue"),lty=1)
	dev.off()
}

findBestKMeans <- function(x,kVal,iters){
	# Takes a data matrix, a k value, and the number of iterations
	# Returns a vector of the best within SS, and the kmeans object
	# Get initial "best" value for SS
	bestVec <- kmeans(x, kVal)
	best <- bestVec$tot.withinss
	for (i in 2:iters) {
		print(paste("Iteration: ", i))
		kData <- kmeans(x, kVal)
		if (kData$tot.withinss < best) {
			best <- kData$tot.withinss
			bestVec <- kData
		}
	}
return(bestVec)
}


makeGraphs(features, kMax, numIterations)
