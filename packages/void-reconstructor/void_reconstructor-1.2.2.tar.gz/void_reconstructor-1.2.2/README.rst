void-reconstructor
------------------

This is a python program that provides the tools for reconstructing the velocities in a LCDM universe using the Jonker-Volgenant algorithm. The input are the positions of the particles in the final configuration. The LAPJV algorithm will then reconstruct the initial positions. Once the initial positions are known, we can calculate the Lagrangian and Eulerian velocities. 

To use this program:

from void-reconstructor import reconstruction as rec
from void_reconstructor.volume_division import *

Then, a Reconstructor object can be created: R = rec.Reconstructor(X_final, ID, masses)


Where X_final is an array of the final positions. For example, if 1000 particles are reconstructed, the shape of X_final is (1000,3) where X_final[:,0] are all x-coordinates for the 1000 particles. 

ID has shape (1000,) and contains a unique number for each particle. This can for example simply be np.range(0,1000). This makes sure that positions, velocities etc. are calculated for the correct particle. 

masses contains the mass for each particle. 

The grid on which the particles are reconstructed can be determined using R.get_grid

------------
Modifications

1.2.0
- Added README
- Fixed an error with mirror_positions()
1.2.2
- Fixed return of box_sizes

