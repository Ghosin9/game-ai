Jake Bowen
Daniel Vu

1. changed the value of "won" to go between 1 and -1 instead of 1 and 0
2. changed rollout() to always pick a victory when possible
3. changed think() to attempt to do all moves that do not have 
a direct loosing child before trying ones that do

Note: the program takes a very long time to execute when using 1000 as num_nodes