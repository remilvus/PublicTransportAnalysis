# PublicTransportAnalysis
This project analyses Krakow's public transport. It tries to answer this 
question: when are public transport vehicles really arriving?  
It's accomplished by using historical data - it allows to compute usual delay 
for every line and also to recreate its schedule.


## Motivation of this project
I started this project, because I wanted to try to find something 
interesting in delays of public transport vehicles. 
For example: maybe there is a bus line which is always delayed by 2 minutes -
if it existed then its schedule could be made more accurate.  

## How it works?
This project consists of 4 parts:

##### Data collectin

This project uses live information about trips (from ftp://ztp.krakow.pl) - 
the files are archived (`scripts/collector.py`) for later analysis.   

##### Data processing
This step should be pretty straightforward - every time a public transportation 
vehicle arrives at a stop its arrival time is saved and its delay is calculated.  
Unfortunately not all provided information is correct - vehicles are usually
reported with wrong id. In most cases it's only possible to determine which line 
a vehicle is serving, but it's hard to tell when a given vehicle should arrive 
at a given stop.   
There is also a problem with provided schedules as they are different from 
the ones [shared by ztp](http://rozklady.ztp.krakow.pl/) - from what I've seen
usually one schedule is shifted by 1 minute, but sometimes the differences are 
a lot more significant (e.g. a few trips could be missing from one schedule).

Because of that a lot of processing have to be done in order to extract any 
information from the data. This is accomplished with:  
- `TableManager` - loads most recent schedules and information about trips
- `TripManager` - keeps track of a given vehicle. This class is responsible
for figuring out the line number that the vehicle is currently serving. It also
checks for any irregularities (e.g. vehicle arriving at a wrong stop) and tries 
to filter incorrect information.
- `StatManager` - provides overall summary of what happened during data 
processing, e.g. how often a vehicle arrived at a stop it wasn't supposed to. 
This exists to help to estimate how much there is of incorrect information.

##### Data analysys

At this step mean delays are calculated and a schedule is extracted by clustering 
recorded arrivals by hdbscan (hierarchical, density-based clustering technique). 
From each cluster mean and minimal values are extracted and 
they can be used as new scheduled time (minimal value is probably better).  

Results of the analysys are saved as a json file



##### Visualisation
todo


## To do:
- imporove trip validation
- make frontend in React