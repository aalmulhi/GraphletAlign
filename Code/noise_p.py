import sys;
import networkx as nx;
import random;

def read_graph(filename):
	edges = [];
	G = nx.Graph();
	#weights = [];
	N = -1;
	index = -1;
	f = open(filename);
	for line in f:
		index += 1;
		l = line.strip().split();
		if index == 0:
			N = int(l[0]);
			continue;
		u = int(l[0]);
		v = int(l[1]);
		G.add_edge(u,v)
		#w = float(l[2]);
		edges.append([u,v]);
		#weights.append(w);

	return G,N,edges;


def main():

	G,N,edges = read_graph(sys.argv[1]);
	p = float(sys.argv[2]);
	removal_count = int(p * float(len(edges)));

	idxes = random.sample(range(len(edges)),removal_count);

	sorted_indexes = sorted(idxes);

	degrees = dict(G.degree());
	new_edges = [];
	j = 0;
	for i in range(len(edges)):
		if j < len(sorted_indexes) and i == sorted_indexes[j]:
			j += 1;
			u = edges[i][0];
			v = edges[i][1];
			if degrees[u] > 1 and degrees[v] > 1:
				G.remove_edge(u,v);
				degrees[u] -= 1;
				degrees[v] -= 1;
			else:					# remove next edge
				if j < len(sorted_indexes)-1 and sorted_indexes[j] + 1  == sorted_indexes[j+1]:		# ignore jth removal
					j += 1;
				else:
					sorted_indexes[j] += 1;
				j -= 1;				# we need to check the current j in next iteration.
			continue;

	new_edges = list(G.edges());

	name = sys.argv[1].strip().rsplit(".",1)[0]+"_Error"+str(p)+".txt";
	f_wr = open(name,'w');
	f_wr.write(str(N)+" "+str(len(new_edges)) );
	for e in new_edges:
		f_wr.write("\n"+str(e[0])+" "+str(e[1]));
	f_wr.close();

main();
