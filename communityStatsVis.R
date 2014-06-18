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

edits_long <- melt(monthlyEdits[,3:5], id="Date")
users_long <- melt(monthlyUsers[,3:6], id="Date")

p <- ggplot(data=edits_long, aes(x=Date, y=value, group=variable, colour=variable))
p <- p + geom_line()
ggsave('monthlyEdits.pdf', p)

p <- ggplot(data=users_long, aes(x=Date, y=value, group=variable, colour=variable))
p <- p + geom_line()
ggsave('monthlyUsers.pdf', p)
