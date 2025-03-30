# Ingress nightmare

## Exploit

Customize the variables at the beginning of xpl.py to your environment.

The script will:

* Spawn a bunch of threads to create a temp files on the container with the shared library containing the reverse shell.
* Spawn a bunch of threads to try guess the correct PID and FD, triggering the loading of the shared library with the corrupted template.

## Reproduce env

Wiz blog offers terraform files to deploy the system in AWS. I personally don't have an account and didn't wanted to pay to deploy it on the cloud, so I'm running this test locally on a minikube env.

### Start cluster with ingress-nginx

`minikube start`

`helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace --version 4.11.3`

### Expose ports

`kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8443:80`

`kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8444:443`

## Open connection

`docker exec -it minikube nc -lvp 4444`

> On minikube, to be sure the container can reach the IP

## Run exploit

`python3 xpl.py`

## POC

![](media/Screenshot%20From%202025-03-30%2013-55-19.png)
![](media/poc.mp4)

## Notes

* For some reason I haven't figured out yet, when uploading a very small library, the file content is cropped in the procfs file (causing a bus error when trying ot execution) so I'm adding some fake functions and compiling with symbols to increase the size, to be sure it won't break.

