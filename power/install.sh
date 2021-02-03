wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -f -p miniconda3
conda init bash
source miniconda3/bin/activate
conda config --add channels conda-forge
conda config --set auto_activate_base false
pip install conda-app
conda-app install mercurial
export PATH=$PATH:$HOME/miniconda3/envs/_env_mercurial/bin

pip install execo

hg clone https://github.com/paugier/nbabel.git

conda install pythran transonic numba clangdev pandas openblas blas-devel requests matplotlib h5py -y
conda create -n env_pypy pypy pandas -y

wget https://julialang-s3.julialang.org/bin/linux/x64/1.5/julia-1.5.3-linux-x86_64.tar.gz
tar -xzf julia-1.5.3-linux-x86_64.tar.gz julia-1.5.3
export PATH=$PATH:$HOME/julia-1.5.3/bin


mkdir $HOME/opt

wget http://buildbot.pypy.org/nightly/map-improvements-3.7/pypy-c-jit-latest-linux64.tar.bz2

tar -xvjf pypy-c-jit-latest-linux64.tar.bz2
rm -f pypy-c-jit-latest-linux64.tar.bz2
mv pypy-c-jit*-linux64 opt/pypy-map-improvements
mkdir -p $HOME/.local/bin
ln -s $HOME/opt/pypy-map-improvements/bin/pypy $HOME/.local/bin/pypy-map-improvements
export PATH=$PATH:$HOME/.local/bin

wget https://buildbot.pypy.org/nightly/py3.7/pypy-c-jit-latest-linux64.tar.bz2
tar -xvjf pypy-c-jit-latest-linux64.tar.bz2
mv pypy-c-jit*-linux64 opt/pypy3.7
ln -s $HOME/opt/pypy3.7/bin/pypy $HOME/.local/bin/pypy-map-improvements
