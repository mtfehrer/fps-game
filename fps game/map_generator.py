import numpy as np
from scipy.spatial import Delaunay
import random

MAP_SIZE = (10, 10)

points = np.array(list({(random.randrange(0, MAP_SIZE[0]), random.randrange(0, MAP_SIZE[1])) for num in range(5)}))

tri = Delaunay(points)

sides = set()
for simplice in tri.simplices:
	for i, s in simplice:
		if simplice[i] != len(simplice) - 1:
			sides.add(s, simplice[i + 1])
		else:
			sides.add(s, simplice[0])

