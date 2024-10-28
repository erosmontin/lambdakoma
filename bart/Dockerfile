# Use a suitable base image with required dependencies
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Install software-properties-common to get add-apt-repository
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update

# Add the Ubuntu Toolchain PPA for newer GCC versions
RUN add-apt-repository ppa:ubuntu-toolchain-r/test && \
    apt-get update

# Install GCC 11 and other necessary packages
RUN apt-get install -y \
    gcc-11 \
    g++-11 \
    make \
    git \
    cmake \
    fftw3-dev \
    liblapacke-dev \
    libopenblas-dev \
    libfftw3-dev \
    libpng-dev \
    libgsl-dev \
    python3 \
    python3-pip \
    libomp-dev \
    tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# Set GCC 11 as the default
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 11 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 11

# Clone the BART repository
RUN git clone https://github.com/mrirecon/bart.git /opt/bart

# Set the working directory
WORKDIR /opt/bart

# Compile and install BART
RUN make

# Set the PATH
ENV PATH="/opt/bart:$PATH"

# Verify BART installation
RUN bart version

# Add deadsnakes PPA and install Python 3.11 and pip
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Create a virtual environment and install pybart
RUN python3.11 -m venv /opt/pybart_env && \
    /opt/pybart_env/bin/pip install numpy scipy matplotlib h5py 
    
RUN /opt/pybart_env/bin/pip install pybart




# Define the entry point for the Docker container
ENTRYPOINT ["bart"]
