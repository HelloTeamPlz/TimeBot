FROM docker.io/pytorch/pytorch

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# set the working directory
WORKDIR /code

ARG gh_username=JaidedAI
ARG service_home="/home/EasyOCR"

# Configure apt and install packages
RUN apt-get update -y && \
    apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    git \
    # cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# Clone EasyOCR repo
RUN mkdir "$service_home" \
    && git clone "https://github.com/$gh_username/EasyOCR.git" "$service_home" \
    && cd "$service_home" \
    && git remote add upstream "https://github.com/JaidedAI/EasyOCR.git" \
    && git pull upstream master

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# Build
RUN cd "$service_home" \
    && python setup.py build_ext --inplace -j 4 \
    && python -m pip install -e .

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# install dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . ./code

#run the bot
CMD ["python3", "bot.py"]