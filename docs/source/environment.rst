Development environment
=======================

First of all, create a directory for your projects. This is where we will
place all the projects, including the **pyphoon** files.

.. code-block:: bash

   mkdir ~/projects


Download library
----------------

Clone the repository and place it in the ``projects`` folder

.. code-block:: bash

   cd ~/projects
   git clone https://github.com/lucasrodes/pyphoon.git



.. _deepo: https://github.com/ufoym/deepo

-----

Docker Setup
------------

For this project a docker container has been used. In particular, we used a
modified version of the docker `deepo`_, which provides a version with GPU
support to most DL/ML frameworks.

If you are unfamiliar with docker you can check the following tutorials:

- `Learn Docker in 12 Minutes 🐳 <https://www.youtube.com/watch?v=YFl2mCHdv24>`_
- `A Quick Introduction to Docker <https://blog.scottlowe.org/2014/03/11/a-quick-introduction-to-docker/>`_

But, basically, what you need to know is that a Docker container is a Virtual
Machine. It is built a Docker image, which you can either create on your own
or download. You can find tons of Docker images at the official Docker
repository, `Docker Hub <https://hub.docker.com/>`_. A Docker container is
fresh and new every time you run it.

Install with GPU support
************************

First, make sure you have installed the `NVIDIA driver <https://github
.com/NVIDIA/nvidia-docker/wiki/Frequently-Asked-Questions#how-do-i-install
-the-nvidia-driver>`_.
Next, we need to install `docker <https://docs.docker
.com/install/linux/docker-ce/centos/>`_ and
`nvidia-docker <https://github.com/NVIDIA/nvidia-docker>`_. Note that by
solely installing ``nvidia-docker`` we automatically install the
last stable release of docker-ce. Hence, all we need to do is install
nvidia-docker.


CentOS/RHEL 7 x86_64
^^^^^^^^^^^^^^^^^^^^

..  code-block:: bash

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

Xenial x86_64
^^^^^^^^^^^^^

..  code-block:: bash

    # If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
    docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
    sudo apt-get purge -y nvidia-docker

    # Add the package repositories
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
      sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/amd64/nvidia-docker.list | \
      sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt-get update

    # Install nvidia-docker2 and reload the Docker daemon configuration
    sudo apt-get install -y nvidia-docker2
    sudo pkill -SIGHUP dockerd

    # Test nvidia-smi with the latest official CUDA image
    docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi


Install without GPU support
***************************

We will be installing docker from the repository for CentOS. For more details
check their `website <https://docs.docker
.com/install/linux/docker-ce/centos/#install-using-the-repository>`_. Make
sure to uninstall other docker versions.


CentOS/RHEL 7 x86_64
^^^^^^^^^^^^^^^^^^^^

..  code-block:: bash

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

Xenial x86_64
^^^^^^^^^^^^^
..  code-block:: bash

    # Uninstall other versions
    sudo yum remove docker docker-common docker-selinux docker-engine
    # Update the apt package index
    sudo apt-get update
    # Install packages to allow apt to use a repository over HTTPS
    sudo apt-get install apt-transport-https ca-certificates curl
    software-properties-common
    # Download and install stable repository
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

Pull Docker image
*****************
Pull the project's docker image from the docker hub:

.. code-block:: bash

   docker pull lucasrodesg/deepo

Creating your Docker Container
******************************

Creating an instance of a Docker image is very simple. The code below is for a
GPU-ready environment, to use it for non-GPU environment simply replace
``nvidia-docker`` by ``docker``.

Let us create a simple container with name "dlnii" using the command ``run``:


..  code-block:: bash

    nvidia-docker run -it --name dlnii lucasrodesg/deepo bash

However, we want our container to have some features:

*   **Port forwarding:** You might want to run some services from within your
    container (e.g. jupyter, tensorboard etc.). Hence, we will make some ports
    available from outside the container by using port-forwarding. This is done
    by using the option ``-p`` when creating the Docker container.
*   **File access:** By default, a Docker container is completely isolated from
    the outside system. However, Docker provides option ``-v`` to enable access
    from container to files in the host machine. This is particularly necessary
    in our case since the scripts in the Docker container need to access the
    dataset files. It works as ``-v <host files path>:<accessible from this
    path in container>``.

All in all, we create the container using

..  code-block:: bash

    nvidia-docker run -it \
    -p <host port>:<container port> \
    -v ~/projects:/root/projects \
    -v /path/to/digital/typhoon/dataset/:/path/to/digital/typhoon/dataset/in/docker/ \
    -v /path/to/new/data/:/path/to/digital/new/data/in/docker/ \
    -v /host/config:/config \
    --name dlnii lucasrodesg/deepo  bash


Let us explain below the different folders made accessible above with option
``-v``:

-   ``/path/to/digital/typhoon/dataset/:/path/to/digital/typhoon/dataset/in/docker/``: Digital Typhoon dataset.
-   ``/path/to/new/data/:/path/to/digital/new/data/in/docker/``:
    Directory where we will store large files. Make sure that you have space.
-   ``~/projects:/root/projects``: The folder containing all the projects
    needs to be accessible from inside the Docker, since we will basically be
    developing code there.

Finally, you can easily instantiate the docker container

..  code-block:: bash

    docker start dlnii


Once started, to execute the instance just type

..  code-block:: bash

    docker exec -it dlnii bash


To exit the container just type

..  code-block:: bash

    exit

Other Docker commands
*********************

To visualize which docker containers are currently running use

..  code-block:: bash

    docker ps -a

This should give you a list of the docker containers with their
respective names, which image they are using, ports etc.

To remove the container

..  code-block:: bash

    docker rm <container name>

Make sure that the container is not running. If that is the case, stop
it using

..  code-block:: bash

    docker stop <container name>
