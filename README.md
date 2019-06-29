# GraphletAlign
Network Alignment using Graphlet Signatureand High Order Proximity

### Overview
In this work, we develop a novel topology-based network alignment approach which we call GraphletAlign.  The  proposed  method  uses  graphlet  signature  as  nodeattributes and then uses a bi-partite matching algorithm for obtainingan initial alignment, which is later refined by considering higher-ordermatching.

### Requirements
python 3.6.8 <br />
lapsolver 1.0.2 <br />
networkx 2.2 <br />

### Running The Code and Input Format 
1. To add noise to the graph run the following: <br />
```
python noise_p.py graph_file noise_percentage
```
2. To generate the graphlet frequencies for the graph use: [Orca Tool](http://www.biolab.si/supp/orca/) <br />
3. To run GraphletAlign code use the following command :<br />
```
python3 GraphletAlign.py graph1_file graphe2_file graph1_graphlet_file graph2_graphlet_file map_file p 
```
