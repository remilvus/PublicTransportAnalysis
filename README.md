# PublicTransportAnalysis
Analysis of Krakow's public transport.  

This project uses live information about trips (from ftp://ztp.krakow.pl) - files are archived (by `collector.py`) 
for later analysis.  

Unfortunately not every field has correct values, thus some of the preprocessing is done in a roundabout way - this 
most probably causes that the results are'nt 100% reliable.  

For now this project allows to generate a map where every stop has a plot which shows mean delay (and std) for every hour.