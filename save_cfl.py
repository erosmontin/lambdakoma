import numpy as np



if __name__ == "__main__":
    # Example usage:
    # Create a sample complex k-space data array
    import glob
    import os
    for npz_file in glob.glob(os.path.join("/g/KOMA/", "**", "*.npz"), recursive=True):
        print(npz_file)
        SL=npz_file.split("/")[-2]
        data=np.load(npz_file)
        os.makedirs(f'/g/BARTD/2/', exist_ok=True)
        save_kspace_bart(data, f'/g/BARTD/2/s{SL}')
