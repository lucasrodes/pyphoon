# Setting up the environment

For this project, a docker container has been used. In particular, we used a
modified version of the docker [deepo](https://github.com/ufoym/deepo), which
 provides a version with GPU support to most DL/ML frameworks. 


## Get the project in your working directory
    
First of all, the project from GitHub should be retrieved. To accelerate the 
work, some symbolic links are created 

*   **Clone the project from GitHub**

    ```
    # Create project folder
    mkdir ~/projects
    # Clone pyphoon
    git clone https://github.com/lucasrodes/pyphoon.git
    ```
    
*   **Create symbolic link to dataset paths**

    ```
    # Go to project workspace
    cd pyphoon
    # Symbolic link to data provided by Digital Typhoon
    ln -s /misc/fs9/datasets/typhoon/wnp/ original_data
    # Create directory where processed/cleaned data will be stored
    mkdir /misc/fs9/<user>/data
    # Symbolic link to the directory
    ln -s /misc/fs9/<user>/data data
    ```
    
    You might want to add `original_data` and `data` to your .gitignore.
    
    
## Pre-requisites

* **Install [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-centos-7)**

    ```
    # Update the package database:
    sudo yum check-update
    # Add the official Docker repository, download the latest version of 
    Docker, and install it:
    curl -fsSL https://get.docker.com/ | sh
    # Start Docker daemon:
    sudo systemctl start docker
    # Verify that it is running
    sudo systemctl status docker
    # Enable it auto-start at every server reboot
    sudo systemctl enable docker
    ```

* **GPU support: Install [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)**
    
    If your machine does not support GPU, ignore this step. 
    
    Make sure you have installed the [NVIDIA driver](https://github.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#how-do-i-install-the-nvidia-driver).
     
    ```
    # If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
    docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
    sudo yum remove nvidia-docker
    
    # Add the package repositories
    curl -s -L https://nvidia.github.io/nvidia-docker/centos7/x86_64/nvidia-docker.repo | \
      sudo tee /etc/yum.repos.d/nvidia-docker.repo
    
    # Install nvidia-docker2 and reload the Docker daemon configuration
    sudo yum install -y nvidia-docker2
    sudo pkill -SIGHUP dockerd
    
    # Test nvidia-smi with the latest official CUDA image
    docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi
    ```


## Creating our Docker Container

*  **Obtain the all-in-one image from [Docker Hub](https://hub.docker.com/r/ufoym/deepo)**
    
    ```
    docker pull ufoym/deepo
    ```
    
*  **Modify image**
    
    Create a Dockerfile

    ```
    mkdir ~/.docker_images/<docker image folder name>
    vim ~/.docker_images/<docker image folder name>/Dockerfile
    ```
    
    and add the following:
    
    ```
    FROM ufoym/deepo
    RUN pip install plotly moviepy jupyter notebook
    ```
    
    Save the file and build the docker image.
    
    ```
    cd ~/.docker_images/<docker image folder name>/
    docker build -t <your_name>/deepo .
    ```
    
    *In the future we plan to generate the docker image and load to the Hub 
    so that other researchers can easily import it.*

*  **Create a Docker container**
    
    Finally, time to create a container of the Docker image. We will create 
    it with GPU name `dlnii` (short for deep learning NII). 
    
    ```
    nvidia-docker run -it 
    -p 8888:8888 \
    -v /misc/fs9/<user>/:/root/storage \
    -v /misc/fs3/home/<user>/projects:/root/projects \
    -v /misc/fs9/datasets/typhoon/wnp/:/root/original_data \
    -v /host/config:/config \
    --name dlnii \
    <your_name>/deepo  bash
    ```
    
    Let us explain below the different options used in the command above.
    
    - `-v`: Enable access from container to files in the host machine.
        In our case, we will make the following files accessible:
    
        - `/misc/fs9/datasets/typhoon/wnp/` accessible from the container as 
        `/root/original_data`. This contains the typhoon data (images and best 
        track)
        - `/misc/fs9/<user>/` accessible as `/root/storage`. This is the 
        directory in the server for `user` to store large files. This is where 
        - `/misc/fs3/home/<user>/projects` accessible from the container as 
        `root/projects`. Note that this assumes that you have a file `projects` 
        in your home directory.
        
    - `-p`: Port forwarding, this is done to access jupyter notebook running 
    from the virtual machine. In particular, we will forward port 8888 in the
     virtual machine to port 8888 in the host machine.
    
    *If your machine does not have GPU-support, run `docker` instead of 
    `nvidia-docker`*

## Create and start Docker container
    
Finally, you can easily instantiate the docker container  

```
docker start dlnii
```

Once started, to execute the instance just type

```
docker exec -it dlnii bash
```

To exit the container just type

```
exit
```

## Docker in Jupyter Notebook

Execute your docker container and run (inside the container):

```
jupyter notebook --ip 0.0.0.0 --allow-root
```

This will prompt with a link of format: `http://0.0.0.0:8888/?token=xxx`. 
Keep the token (xxx). Now, navigate to [localhost:8888](localhost:8888) in 
your web browser in the host machine. Use the token as the password.

Create a notebook and start coding, it will run on the docker!

    
