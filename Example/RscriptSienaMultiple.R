###################   RscriptMultipleSiena.R  #############################
# This is a script illustrating multivariate dependent networks for RSiena.
# Written by Tom A.B. Snijders
#
#                      version Sept 27, 2010


#####  Reading Data
# These data are totally manufactured and serve only as illustration.

a1 <- as.matrix(read.table("aadv_t1.txt",header=F))
a2 <- as.matrix(read.table("aadv_t2.txt",header=F))
t1 <- as.matrix(read.table("ttr_t1.txt",header=F))
t2 <- as.matrix(read.table("ttr_t2.txt",header=F))
hi <- as.matrix(read.table("hier.txt"))


#### Defining RSiena variables

library(RSiena)
advice <- sienaNet(array(c(a1,a2), dim=c(49,49,2)))
trust  <- sienaNet(array(c(t1,t2), dim=c(49,49,2)))
hierarchy <- coDyadCovar(hi)

# We just give the two networks to sienaDataCreate.
# They have the same dimensions; this is necessary,
# as they have the same nodeSet.

multidata <- sienaDataCreate(advice,trust,hierarchy)
multieff <- getEffects(multidata)

# If you wish, you can have a look at multieff
# Pay attention to the 'name' column,
# which is the name of the dependent variable.
# 
# fix(multieff)

print01Report(multidata,multieff,modelname="two_networks")


### Specifying the model

# Here we must also give the name of the dependent variable
# when calling functions such as includeEffects().
# The default name is the first in the list of networks
# mentioned in the call of sienaDataCreate (here: advice).

multieff <- includeEffects(multieff,transTrip,cycle3,inPopSqrt,outActSqrt,inActSqrt,name="advice")
multieff <- includeEffects(multieff,transTrip,cycle3,inPopSqrt,outActSqrt,inActSqrt,name="trust")
multieff <- includeEffects(multieff,X,name="trust",interaction1="hierarchy")

# There are some additional effects for multiple networks, 
# expressing how the networks affect one another.
# These can be found in the manual.
# To find out their shortName you may use the following commands

sink("multi_effects.txt")
cbind(multieff[,'effectName'],multieff[,'shortName'])
sink()

# The effectNames are more comprehensible than the shortNames,
# and in the manual the effects are given with their effectNames
# (shortNames are still to be added ...)
# Not all effects listed are implemented yet.
# In the first call to includeEffects as shown below,
# crprod (for crossproduct) expresses the direct effect of trust on advice;
# crprodRecip expresses the effect of trust on reciprocal advice;
# from expresses the effect from agreement on trust 
# (i.e., trusting the same third parties) to advice.

multieff <- includeEffects(multieff,crprod,crprodRecip,from,
                             name="advice",interaction1="trust")
multieff <- includeEffects(multieff,crprod,crprodRecip,from,
                             name="trust",interaction1="advice")

# Check the specified model:
multieff

# Create the object with settings for the algorithm,
# and estimate:

multimodel <- sienaModelCreate(projname = 'two_networks' )
multians <- siena07(multimodel, data = multidata, effects = multieff)

# Inspect the results (also in file two_networks.out):
multians
###################################################################################

