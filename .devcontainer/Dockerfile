# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.234.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# FROM igormaraujo/lpsolve-python3

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
#ARG NODE_VERSION="none"
#RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi


 #Majority from: https://github.com/igormaraujo/docker-lpsolve-python3/blob/master/Dockerfile
# Copy install files to tmp dir
COPY .devcontainer/fix-lpsolve.patch /tmp

# Install dependences
RUN apt-get update && apt-get install -y \
	wget \
	git \
	gcc \
	zip \
	&& rm -rf /var/lib/apt/lists/*

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY ../requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
#RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends lpsolve

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1


# Set environment variables
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/lp_solve_5.5/lpsolve55/bin/ux64
ENV PATH=$PATH:/opt/lp_solve_5.5/bin/ux64

# Download, compile and install lp-solve with Python 3x Interface
RUN wget https://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.5/lp_solve_5.5.2.5_source.tar.gz \
  && tar -xvf lp_solve_5.5.2.5_source.tar.gz \
  && mv lp_solve_5.5 /opt \
  && git clone https://github.com/igormaraujo/lp_solve_python_3x.git \
  && mv lp_solve_python_3x/extra /opt/lp_solve_5.5 \
  && rm -rf lp_solve_python_3x lp_solve_5.5.2.5_source.tar.gz \
  && cd /opt/lp_solve_5.5/lpsolve55 \
  && patch -f < /tmp/fix-lpsolve.patch \
  && sh ccc \
  && cd /opt/lp_solve_5.5 && mkdir -p bin/ux64 && cd bin/ux64 \
  && wget https://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.5/lp_solve_5.5.2.5_exe_ux64.tar.gz \
  && tar -xvf lp_solve_5.5.2.5_exe_ux64.tar.gz \
  && mv *.so /opt/lp_solve_5.5/lpsolve55/bin/ux64 \
  && rm -rf lp_solve_5.5.2.5_exe_ux64.tar.gz \
  && cd /opt/lp_solve_5.5/extra/Python \
  && python setup.py install \
  && rm -rf /tmp/fix-lpsolve.patch /tmp/requirements.txt \
  && mkdir /home/$NB_USER/examples/
