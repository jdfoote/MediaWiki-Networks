require(Hmisc)
require(yaml)

config <- yaml.load_file('~/Programming/WeRelate/Code/config.yaml')
statsColsToInclude <- c(40,41,48:55)

stats <- as.data.frame(read.csv('~/Programming/WeRelate/DataFiles/allUserStatsRatios0Trailing.csv',stringsAsFactors=FALSE))
stats[,4:41] <- apply(stats[,4:41], 2, function(x) as.numeric(x))
stats$kMedCluster <- as.factor(stats$kMedCluster)

stats$simple_total <- rowSums(stats[,c(config$editCats$simple_edits)])
stats$community_talk_total <- rowSums(stats[,c(config$editCats$community_talk_edits)])
stats$community_total <- rowSums(stats[,c(config$editCats$community_edits)])
stats$complex_total <- rowSums(stats[,c(config$editCats$complex_edits)])
stats$other_total <- rowSums(stats[,c(config$editCats$other_edits)])
stats$local_talk_total <- rowSums(stats[,c(config$editCats$local_talk_edits)])
stats$logged_edits <- (log(stats$all_edits+1))
stats$logged_manual_edits <- (log(stats$manual_edits + 1))

clusterMeans <- aggregate(stats[,statsColsToInclude], by=list(stats$kMedCluster), FUN=mean)
clusterMedians <- aggregate(stats[,statsColsToInclude], by=list(stats$kMedCluster), FUN=median)


# These provide the basis for the tables, which I cleaned up manually
latex(format.df(t(clusterMeans), dec=3), file="means.tex", title="Cluster Means")
latex(format.df(t(clusterMedians), dec=3), file="medians.tex", title="Cluster Medians")

# This calculates the stats for each cluster, which I just added to the table
# number of user-months
print(table(stats$kMedCluster))
# number of unique users
print(length(unique(stats[stats$kMedCluster == 0,]$user_id)))
print(length(unique(stats[stats$kMedCluster == 1,]$user_id)))
print(length(unique(stats[stats$kMedCluster == 2,]$user_id)))
print(length(unique(stats[stats$kMedCluster == 3,]$user_id)))

