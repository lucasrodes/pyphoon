Find a list of tasks to do

- [ ] Clean data (L)
- [ ] Prepare dataset for first task: TC vs extra-TC classifier (L)
- [ ] Supervise documentation 
- [ ] Enable notebook in NII server


nvidia-docker run -it \
-p 9999:9999 \
-p 10000:10000 \
-p 10001:10001 \
-v ~/projects:/root/projects \
-v /fs9:/root/fs9 \
-v /host/config:/config \
--name luke lucasrodesg/deepo  bash