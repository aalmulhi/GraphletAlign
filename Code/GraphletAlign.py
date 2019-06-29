'''
Author: Aljohara Almulhim
LOD 2019
IUPUI 2019
'''

import sys;
import networkx as nx;
from numpy import linalg as LA
import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import accuracy_score
import math;
import datetime;
from sklearn.neighbors import KDTree
from scipy import sparse
import csv
from operator import itemgetter
from lapsolver import solve_dense

#load graph filess
def load_graph(file2read):
        index = -1;
        G = nx.Graph();
        for line in file2read:
                index += 1;
                if index == 0:
                        continue;
                l = line.strip().split();
                G.add_edge(int(l[0]),int(l[1]));
        return G;

#load graphlet file
def load_graphlet(filetoread):
        index = 0;
        N = 0;
        data = [];
        for line in filetoread:
                if index == -1:
                        line = line.strip().split();
                        N = int(line[0]);
                        data = [[]]*N;
                        index +=1;
                        continue;
                line = line.strip().split();
                d = list(map(float,line))
                #norm_d = np.array(d) / max(d);
                log_d= [np.log(i) if i!=0.0 else (i) for i in d]
                data.append(log_d); 
                #data.append(norm_d);                       
                index += 1;
        return np.array(data);

#True Assignment (Mapping File)
def load_map(f):
        lines=f.readlines()
        lines=lines[1:]
        map_d=[]
        for x in lines:
            map_d.append(int(x.split(' ')[1]))
        f.close()
        
        return np.array(map_d, dtype=np.int32)

#Calculate L2 Norm for cost matrix 1 - with kd tree
def kd_tree_map(N1,N2,g1_features,g2_features,top_n):
        cost_m= np.full((N1, N2), np.nan)
        tree = KDTree(g2_features)
        dist, ind = tree.query(g1_features, k=top_n)
        for i in range(N1):
                for nbr in range(top_n):
                        j=ind[i,nbr]
                        dst= dist[i,nbr]
                        cost_m[i,j]=dst
        return cost_m

#Calculate L2 Norm for cost matrix 2 - with Nbr. info
def calc_cost2(N1,N2,cost_m,G1,G2,mapping,reverse_map):
        # second hop costs
        cost_m2=np.zeros((N1,N2), dtype=np.float)
        for i in range(N1):
                nei_node1 = list(G1.neighbors(i));

                map_nei_node1 = mapping[nei_node1];
                for j in range(N2):
                        nei_cost_sum = 0.0;
                        nei_node2 = list(G2.neighbors(j));

                        diff2_1 = set(map_nei_node1) - set(nei_node2);
                        diff1_2 = set(nei_node2) - set(map_nei_node1);

                        count_cost = len(diff1_2 | diff2_1);
                        avg_nei_cost = (2.0*count_cost) / float(len(nei_node1)+len(nei_node2));

                        cost_m2[i,j]= cost_m[i,j] + avg_nei_cost;

        sys.stdout.flush();

        return cost_m2


def main():
        if len(sys.argv) < 7:
                print ("enter graph_file1 graph_file2 graphlet_file1 graphlet_file2 map_file nbr");
        else:
                graph_file1 = open(sys.argv[1]);
                graph_file2 = open(sys.argv[2]);
                graphlet_file1 = open(sys.argv[3]);
                graphlet_file2 = open(sys.argv[4]);
                map_file= open(sys.argv[5]);
                top_n= int(sys.argv[6])
        name1 = sys.argv[1].strip().rsplit(".",1)[0].strip().rsplit("/",1)[-1];
        name2 = sys.argv[2].strip().rsplit(".",1)[0].strip().rsplit("/",1)[-1];
        nn = "sparse_cost."+name1+'.'+name2+'.txt'

        G1 = load_graph(graph_file1);
        G2 = load_graph(graph_file2);
        data1 = load_graphlet(graphlet_file1);
        print (data1.shape)
        data2 = load_graphlet(graphlet_file2);
        print (data2.shape)
        map_data = load_map(map_file);
        N1= data1.shape[0];
        N2= data2.shape[0];
        
        sys.stdout.flush();
        start_tot= datetime.datetime.now();
        #C1: calculate L2-norm cost using kd-tree
        start_t = datetime.datetime.now();
        cost_m1= kd_tree_map(N1,N2,data1,data2,top_n)
        end_t = datetime.datetime.now();
        print ("time for distance based cost cal. using kd-tree: "+str((end_t - start_t).total_seconds()));

        #M1: mapping using lapsolver
        print ("mapping1 - using lapsolver:")
        row_ind=[]
        col_ind=[]
        start_t = datetime.datetime.now();
        row_ind, col_ind=  solve_dense(cost_m1)
        end_t = datetime.datetime.now();
        print ("time for mapping1= "+ str((end_t - start_t).total_seconds()))
        print ("cost1=",cost_m1[row_ind, col_ind].sum())
        print ("Number of mapped items:",len(row_ind))
        acc1= accuracy_score(map_data, col_ind)
        print ("---------------------------------------------")
        print ("accuracy=",acc1)
        print ("---------------------------------------------")

        #revers mapping
        reverse_map = {};
        for i in range(len(col_ind)):
                reverse_map[col_ind[i]] = i;

        #C2: claculate 2nd hop cost matrix
        start_t = datetime.datetime.now();
        cost_m2 = calc_cost2(N1,N2,cost_m1,G1,G2,col_ind,reverse_map);
        end_t = datetime.datetime.now();
        print ("time for distance based cost cal. using 2nd hop: "+ str((end_t - start_t).total_seconds()))
        #M2: mapping using lapsolver
        print ("mapping2 - using lapsolver:")
        start_t = datetime.datetime.now();
        row_ind2, col_ind2 = solve_dense(cost_m2)
        end_t = datetime.datetime.now();
        print ("time for mapping2= "+ str((end_t - start_t).total_seconds()))
        end_tot= datetime.datetime.now();
        print ("cost2=",cost_m2[row_ind2, col_ind2].sum())
        print ("Number of mapped items:",len(row_ind2))
        print ("---------------------------------------------")
        np.savetxt("output/mapping_"+nn+str(top_n)+"txt", np.column_stack((row_ind2,col_ind2)), delimiter=",", fmt='%i')

        #accuracy true_mapping vs. linear_sum_assignment
        asg_m = list(zip(row_ind2, col_ind2))
        map_ind= list(range(len(map_data)))
        map_m = list(zip(map_ind, map_data))

        asg_m_ind= [i[0] for i in asg_m]
        map_m_mod = [i for i in map_m if i[0] in asg_m_ind]
                     
        actual_y= [i[1] for i in map_m_mod]
        pred_y= [i[1] for i in asg_m]
                                 
        acc2= accuracy_score(actual_y, pred_y)
        print ("accuracy=",acc2)
        print ("---------------------------------------------")
        print ("total time:", str((end_tot - start_tot).total_seconds()))
        
main();

