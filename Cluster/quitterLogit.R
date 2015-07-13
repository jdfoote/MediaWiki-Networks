library(stargazer)
# I randomly selected a month to focus on. We will look at the activity in the previous 3 months
# to see what predicts quitting in this month.
focusMonth = as.Date('2012-07-03')
d <- as.data.frame(read.csv("~/Programming/WeRelate/DataFiles/allUserStatsRatios0Trailing.csv"))
dSmall <- d[c(1,3,41,44,45)]
dSmall$kMedCluster[dSmall$kMedCluster == '0'] <- 'LowActivity'
dSmall$kMedCluster[dSmall$kMedCluster == '1'] <- 'CentralMember'
dSmall$kMedCluster[dSmall$kMedCluster == '2'] <- 'PeripheralExpert'
dSmall$kMedCluster[dSmall$kMedCluster == '3'] <- 'Newbie'
dSmall$end_date <- as.Date(dSmall$end_date)
# Note - this gets the 3 months before the focus month, plus the focus month
dSmaller <- subset(dSmall, end_date > focusMonth - 95 & end_date < focusMonth + 1)
# Make wide
dw <- reshape(dSmaller, idvar="user_id", timevar="end_date", direction="wide")
# Remove users who weren't active in the month before`
dw <- dw[!is.na(dw[,9]) && dw[,9] > 0]
# Mark as quitters those without a measurement for this month, or who did nearly nothing
dw$quitter <- is.na(dw[,13])|dw[,13] < 2
# Rename some columns to make them easier to access and understand output
colnames(dw)[c(3,6,9,8)] = c('ThreeBefore','TwoBefore','OneBefore','daysSinceJoining')
# Replace NAs
dw[,c(3,6)][is.na(dw[,c(3,6)])] <- 'NotYetJoined'
dw$ThreeBefore <- factor(dw$ThreeBefore, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert","NotYetJoined"))
dw$TwoBefore <- factor(dw$TwoBefore, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert","NotYetJoined"))
dw$OneBefore <- factor(dw$OneBefore, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert"))
mylogit <- glm(quitter ~ OneBefore + TwoBefore + ThreeBefore + daysSinceJoining, data=dw, family="binomial")
print(summary(mylogit))
stargazer(mylogit, out="quitterLogit.tex")
