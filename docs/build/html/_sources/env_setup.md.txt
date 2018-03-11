# Setting up the environment

For this project and others that are based on this, a docker container has been 
used. In particular, we used a modified version of the docker [deepo](https://github.com/ufoym/deepo), 
which provides a version with GPU support to most DL/ML frameworks. 

If you are unfamiliar with docker you can check the following tutorials:

- [Learn Docker in 12 Minutes 🐳](https://www.youtube.com/watch?v=YFl2mCHdv24)
- [A Quick Introduction to Docker](https://blog.scottlowe.org/2014/03/11/a-quick-introduction-to-docker/)

But, basically, what you need to know is that a Docker container is a Virtual
 Machine. It is built a Docker image, which you can either create on your own
  or download. You can find tons of Docker images at the official Docker 
  repository, [Docker Hub](https://hub.docker.com/). A Docker container is 
  fresh and new every time you run it.
 
**Note:** Be aware that some of the commands might require sudo permission


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
    
    
## Docker

*   **GPU support**

    First, make sure you have installed the [NVIDIA driver](https://github.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#how-do-i-install-the-nvidia-driver).
    Next, we need to install [docker](https://docs.docker.com/install/linux/docker-ce/centos/) and 
    [nvidia-docker](https://github.com/NVIDIA/nvidia-docker). Note that by 
    solely installing `nvidia-docker` we automatically install the 
    last stable release of docker-ce. Hence, all we need to do is install 
    nvidia-docker.
    
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

*   **No-GPU support**
    
    We will be installing docker from the repository for CentOS. For more 
    details check their [website](https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository).
    
    Make sure to uninstall other docker versions
    
    ```
    # Uninstall other versions
    sudo yum remove docker docker-common docker-selinux docker-engine
    # Install required packages
    sudo yum install -y yum-utils device-mapper-persistent-data lvm2
    # Set up stable repository
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    # Make sure to disable edge versions, otherwise nvidia-docker will not recognize docker
    sudo yum-config-manager --disable docker-ce-edge
    # Install docker-ce
    sudo yum install docker-ce
    ```


## Creating our Docker Container

*  **Obtain the all-in-one image from [Docker Hub](https://hub.docker.com/r/ufoym/deepo)**
    
    ```
    docker pull lucasrodesg/deepo
    ```
    
    Details on how we generated this image can be found [here](create_docker_image.html).
    
*  **Create a Docker container**
    
    Finally, time to create a container of the Docker image. We will create 
    it with GPU name `dlnii` (short for deep learning NII). 
    
    ```
    nvidia-docker run -it \
    -p <host port>:<container port> \
    -v /misc/fs9/<user>/:/root/storage \
    -v /misc/fs3/home/<user>/projects:/root/projects \
    -v /misc/fs9/datasets/typhoon/wnp/:/root/original_data \
    -v /host/config:/config \
    --name dlnii \
    lucasrodesg/deepo  bash
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
        
        **Note:** You might want to have direct access to the data. In that 
        case use `-v /misc/fs9/lucas/data/:/root/data`.
        
    - `-p`: Port forwarding, this is done to access Jupyter Notebook running 
    from the virtual machine (more on this below). Make sure to use a free 
    port. I used same for host and container, namely `9999`. Make sure that 
    there is no other service (including docker images) using that port!
    
    **Note:** If your machine does not have GPU-support, run `docker` instead
     of `nvidia-docker`

*  **Create and start Docker container**
        
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

*   **Helpful Docker commands**
    
    To visualize which docker containers are currently running use
    
    ```
    docker ps -a
    ```
    
    This should give you a list of the docker containers with their 
    respective names, which image they are using, ports etc.
    
    To remove the container
    
    ```
    docker rm <container name>
    ```
    
    Make sure that the container is not running. If that is the case, stop 
    it using
    
    ```
    docker stop <container name>
    ```

## Run Jupyter Notebook in your localhost from Docker!

The main idea is to port forward from your host machine until the docker 
virtual environment.

You basically need to use 

```
ssh -L <host port>:localhost:<remote host port> remote_host
```

Note that if you are connected through various ssh you need to run that for 
each of them. Then, **in your Docker virtual environment** run

```
jupyter notebook --ip 0.0.0.0 --port <container port> --allow-root
```

This will prompt with a link of format: `http://0.0.0.0:<container port>/?token=xxx`. 
Keep the token (xxx). Now, navigate to localhost:<host port> in your host 
machine and use the token as the password.

Create a notebook and start coding, it will run on the docker!

    

