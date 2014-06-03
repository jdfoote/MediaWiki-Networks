d <- as.data.frame(read.csv("../DataFiles/clustersByID0Trailing.csv"))
d$isCentral <- apply(d, 1, function(x) sum(x[5:76]=='1',na.rm=TRUE)>=2)
dSmall <- d[,c(2,3,4,77)]
xtabs(~isCentral+T1, data=d1Small)
xtabs(~isCentral+T2, data=d1Small)
xtabs(~isCentral+T3, data=d1Small)
dSmall[dSmall == '0'] <- 'LowActivity'
#dSmall[is.na(dSmall)] <- 'LowActivity'
dSmall[dSmall == '1'] <- 'CentralMember'
dSmall[dSmall == '2'] <- 'PeripheralExpert'
dSmall[dSmall == '3'] <- 'Newbie'
dSmall$T1 <- factor(dSmall$T1, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert"))
dSmall$T2 <- factor(dSmall$T2, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert"))
dSmall$T3 <- factor(dSmall$T3, ordered=FALSE, levels=c("LowActivity","CentralMember","Newbie","PeripheralExpert"))
mylogit <- glm(isCentral ~ T1 + T2 + T3, data=dSmall, family="binomial")
print(summary(mylogit))
