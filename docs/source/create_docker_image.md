# Modifying existing docker image

Sometimes, an existing docker image might be close to what we want but might be
lacking on some libraries. To overcome this, you can easily modify an existing 
docker image.

*   **Pull base image**

    To modify an existing image first pull the base image you want to modify
    
    ```
    docker pull <base image name>
    ```

*  **Modify image**
    
    Next, create a Dockerfile

    ```
    # Create docker images folder
    mkdir ~/.docker_images
    # Create folder for new docker image
    mkdir ~/.docker_images/<docker image folder name>
    # Create docker file
    vim ~/.docker_images/<docker image folder name>/Dockerfile
    ```
    
    and add the libraries that you want to install. Say you want to
    install `plotly`:

    ```
    FROM <base image name>
    RUN pip install plotly
    ```

    Save the file and build the docker image.
    
    ```
    cd ~/.docker_images/<docker image folder name>/
    docker build -t <modified image name> .
    ```

*   **Upload image to Docker hub**

    First make sure that you have an account in [Docker Hub](https://hub.docker.com/).
    Next, follow the steps [here](https://docs.docker.com/docker-cloud/builds/push-images/) to
    push your image.