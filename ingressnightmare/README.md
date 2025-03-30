
## Reproduce

### Start cluster with ingress-nginx

`minikube start`
`helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace --version 4.11.3`

### Expose ports

`kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8443:80`
`kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8444:443`
