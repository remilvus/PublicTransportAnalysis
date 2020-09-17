# PublicTransportAnalysis
Analysis of Krakow's public transport.  

## Motivation of this project
I started this project, because I was interested if there is anything 
interesting waiting to be found in delays of public transport vehicles. 
For example: maybe there is a bus line which is always delayed by 2 minutes and
 its schedule can be made more accurate.  

## How it works?
This project uses live information about trips (from ftp://ztp.krakow.pl) - 
files are archived (by `collector.py`) for later analysis.  

Unfortunately not all provided information is correct - because of that 
some of the preprocessing is done in a roundabout way (for this reason 
the results aren't 100% reliable). The main problem is that not all vehicles
have correctly assigned route - this information is validated by comparing the 
set of stops visited by a vehicle with known routes.  

## Result
For now this project generates a map where every stop has delays for its 
lines visualised on a plot (mean and std per hour).  
Example output: `map_example_small.html` (it covers only a small portion
of all stops as the complete map is quite big - over 100MB).

## To do:
- better trip validation
- Frontend in React