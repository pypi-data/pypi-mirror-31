
# nx_altair

*Draw NetworkX graphs with Altair*

**nx_altair** offers a similar **draw** API to NetworkX but returns Altair Charts instead.


```python
import networkx as nx
import nx_altair as nxa

# Generate a random graph
G = nx.fast_gnp_random_graph(n=20, p=0.25)

# Compute positions for viz.
pos = nx.spring_layout(G)

# Draw the graph using Altair
viz = nxa.draw_networkx(G, pos=pos)

# Show it as an interactive plot!
viz.interactive()
```

<img src="docs/_img/readme.png" width="350">

nx_altair also supports many of the same arguments from NetworkX for styling your network.

```python
import networkx as nx
import nx_altair as nxa
import numpy as np

# Generate a random graph
G = nx.fast_gnp_random_graph(n=20, p=0.25)

# Add weights to nodes and edges
for n in G.nodes():
    G.nodes[n]['weight'] = np.random.randn()

for e in G.edges():
    G.edges[e]['weight'] = np.random.uniform(1, 10)

# Compute positions for viz.
pos = nx.spring_layout(G)

# Draw the graph using Altair
viz = nxa.draw_networkx(
    G, pos=pos,
    node_color='weight',
    cmap='viridis',
    width='weight',
    edge_color='black',
)

# Show it as an interactive plot!
viz.interactive()
```
<img src="docs/_img/readme2.png" width="450">


## Install

To install from PyPI:

```
pip install nx_altair
```

To install for development, clone this repos and install using pip
```
pip install -e .
```

## Contributing

We welcome pull requests! If you find a bug, we'd love for you to submit a PR. If you're not sure how to do that, check out this [simple guide](https://github.com/Zsailer/guide-to-working-as-team-on-github).

If you have a feature request, please open an issue or submit a PR!


