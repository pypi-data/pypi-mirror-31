# To build this docker image run the following command from directory containing Dockerfile:
#     docker build -t isoenum .

FROM fedora:27

MAINTAINER	Andrey Smelter

# Copy isoenum code to the root directory and set working directory
COPY . /isoenum/
WORKDIR /isoenum

# Install python
RUN dnf update -y
RUN dnf install python3 -y
RUN dnf install python3-pip -y

# Install Open Babel
RUN dnf install openbabel -y

# Install isoenum python requirements
RUN pip3 install -r /isoenum/requirements.txt

# Set entry point
ENTRYPOINT [ "python3", "-m", "isoenum" ]

# docker run -v /run/media/smelandr/7ABCF9FD15922165/My\ Data/Documents/University\ of\ Kentucky/Projects/nmr_metabolite_naming/isoenum/tests/example_data/bmse000040.sdf:/isoenum/bmse40.sdf -v /home/smelandr/Desktop/sdfile.sdf:/isoenum/sdfile.sdf -t isoenum name /isoenum/bmse40.sdf -a C-13 -o /isoenum/sdfile.sdf -r sdf