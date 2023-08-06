paths_graph
===========

.. image:: https://travis-ci.org/johnbachman/paths_graph.svg?branch=master
    :target: https://travis-ci.org/johnbachman/paths_graph
.. image:: https://coveralls.io/repos/github/johnbachman/paths_graph/badge.svg?branch=master
    :target: https://coveralls.io/github/johnbachman/paths_graph?branch=master

A graph-based representation of path ensembles in directed graphs.

In many types of networks, edges indicate the direction of causal
relationships. Causal flows are therefore captured by `paths`.
entities, the flow of causal influences are captured by paths. Analysis of
biological relationships in these networks therefore often amounts to studying
collections of paths and their properties. A key challenge is analyzing these
relationships is is that enumerating paths between nodes of interest can be
computationally challenging due to the combinatorial explosion of paths as
length increases. One common strategy for addressing this involves searching
for shortest paths using breadth first search or Dijkstra’s algorithm. However,
biological networks generally contain indirect edges bypassing key regulators.
As a result the most meaningful paths may be considerably longer than the
shortest path. In addition, the full set of paths may not be relevant: one may
only want to explore paths that meet additional biological constraints (e.g.,
paths passing through a protein of interest).

Motivated by these considerations we have constructed a data structure called
the Cycle Free Paths Graph (CFPG) which represents the set of paths of interest
without explicitly enumerating them. Using the CFPG, queries concerning a set
of paths can be answered by performing graphical operations on the CFPG rather
than on the underlying biological network. Our construction of a CFPG takes as
input, a biological network consisting of directed graph G, a source node S, a
target node T and path lengths of interest ranging from Lmin to Lmax. We
describe here the constuction for unsigned graphs; the procedure for signed
graphs, in which both edges and paths have polarities, is similar.

For each path length l in [Lmin, Lmax] a CFPG for l (representing the
cycle-free paths of length l from S to T in G) is constructed in two steps.
First, a directed acyclic graph called a paths graph (PG) that represents all
S-T paths (i.e. which may contain cycles) of length l is constructed. The key
to this first step is the observation that the intersection of the set of nodes
that can be reached forwards from S in exactly k steps with the set of nodes
that can be reached backwards from T in exactly l − k steps will all lie in
position k of l-length paths from S to T in G. A node v which lies in this
intersection will appear as the node (k,v) in the paths graph. In addition,
there will be an edge from (i,u) to (j,v) in the paths graph if j = i+1 and
(u,v) is an edge in G. In Figure 4 we show a small random graph G and a paths
graph PG representing all paths of length 5 in G from the source node B to the
target node D. We note that (0, F) is the unique start node and (5, D) is the
unique terminal node of PG.

In the second step we transform PG into a cycle-free paths graph CFPG by adding
a suitable amount of ‘history’ information to the nodes in PG. Informally,
(i,v,h) is a node in CFPG if (i,v) is a node in PG and h is the set of nodes in
the past of (i, v) in PG through which one can reach (i, v) from (0, S) without
encountering a cycle. We add an edge from (i, u, hu) to (i + 1, v, hv) provided
there is an edge from (i, u) to (i+1, v) in PG and the history hu is included
in hv. This construction guarantees there is a one-to-one correspondence
between the set of cycle-free paths of length l between S and T in G and the
set of paths from the unique start node to the unique terminal node of CFPG
(Figure 4).

A variety of analysis tasks can be performed by exploiting the graphical
structure of CFPGs. In particular, quantitative properties of the distribution
of cycle-free paths between S and T can be efficiently obtained by sampling
from the CFPG under different assumptions regarding edge weights. CFPGs
computed over different lengths can be merged and then sampled to yield the
distribution of paths of different lengths. Boolean operations on CFPGs can be
performed to represent sets of paths under a variety of constraints: for
example, given a CFPG representing paths passing through a node u, and another
representing paths avoiding a different node v, a CFPG can be easily computed
to represent the cycle-free paths from S to T that pass through u but avoid v.
