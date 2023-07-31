# Guide to test usage of Ray to serve models

This guide will describe how to deploy using Ray Serve the model used in the simplified LLM chain.

## Install the Python requirements
Create a virtual environment that will be used to log the model into mlflow:
```shell
python3 -m venv .rayenv
```

Activate that virtual environment and install the requirements:
```shell
source .rayenv/bin/activate
pip install -r requirements.txt
```
Note it is important to make sure that ray version in if fact 2.6.1, as it contains an important patch. To check the version of ray, do:
```shell
ray --version
```

## Start Ray cluster
It was chosen to deploy the model. To achieve that, you need to deploy it on a Ray cluster. To start a local Ray cluster execute the following command:
```shell
ray start --head
```

## Deploy the model
If you do not have any GPU available, you may need to modify the file [config.yaml](./config.yaml) to remove the `num_gpus` in Ray actor options. You can also define in that file the port at which to serve the models. Then you can execute:
```shell
serve deploy config.yaml
```

This should normally deploy the models.


To stop serving the model, you can execute:
```shell
ray stop
```

To exit the vistual environment, you can execute:
```shell
deactivate
```
