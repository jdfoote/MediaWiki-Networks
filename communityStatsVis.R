require(ggplot2)
require(reshape2)

# Load files
monthlyEdits <- as.data.frame(read.csv('MonthlyEdits.csv'))
monthlyNew <- as.data.frame(read.csv('monthlyNew.csv'))
monthlyActive <- as.data.frame(read.csv('monthlyActive.csv'))

# Prepare files
monthlyEdits <- monthlyEdits[order(monthlyEdits$yyyy,monthlyEdits$mon),]
monthlyNew <- monthlyNew[order(monthlyNew$yyyy,monthlyNew$mon),]
monthlyActive <- monthlyActive[order(monthlyActive$yyyy,monthlyActive$mon),]
monthlyUsers <- monthlyActive
monthlyUsers$New.Users <- monthlyNew$New.Users

monthlyEdits$Cumulative.Edits <- cumsum(monthlyEdits$Edits)
monthlyEdits <- transform(monthlyEdits, Date = as.Date(paste(yyyy, mon, 1, sep = "-")))

monthlyUsers$Cumulative.Users <- cumsum(monthlyUsers$New.Users)
monthlyUsers <- transform(monthlyUsers, Date = as.Date(paste(yyyy, mon, 1, sep = "-")))

edits_long <- melt(monthlyEdits[,c(3,5)], id="Date")
users_long <- melt(monthlyUsers[,c(3,4,6)], id="Date")

p <- ggplot(data=edits_long, aes(x=Date, y=value, group=variable, colour=variable))
p <- p + geom_line()
p <- p + scale_color_discrete(name="")
p <- p + ylab("Number of edits")
ggsave('monthlyEdits.pdf', p)

p <- ggplot(data=users_long, aes(x=Date, y=value, group=variable, colour=variable))
p <- p + geom_line()
p <- p + scale_color_discrete(name="User Type", breaks=c("Active.Users", "New.Users"), labels=c("All Active Users", "New Users"))
p <- p + ylab("Number of users")
ggsave('monthlyUsers.pdf', p)
