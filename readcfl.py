import numpy as np




# Example usage:
# Read a sample .cfl file
SL=88
#docker run --mount type=bind,source=/g/BARTD,target=/cfl -it --entrypoint /bin/bash docker.io/biocontainers/bart:v0.4.04-2-deb_cv1
#  bart fft -i 7 /cfl/2/s90 s; bart rss 8 s s2 ; bart toimg s2 /cfl/2/r90

data = read_cfl(f'/g/BARTD/{SL:02d}o')

import matplotlib.pyplot as plt
plt.imshow(np.abs(np.sum(data[0,0,0,0,0,0,0,0,0,0,0,0,0],axis=-1)), cmap='gray',)

plt.title(f'Reconstructed Image BART')
plt.colorbar()
plt.savefig(f'RSS{SL:02d}.png',dpi=300)
plt.show()
