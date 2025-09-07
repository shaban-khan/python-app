# Application Validation and Traffic Flow in AKS

This document provides a knowledge base for validating your application deployed in **Azure Kubernetes Service (AKS)** with NGINX Ingress Controller and TLS.  

---

## 1️⃣ Validate Application Inside AKS

These checks confirm that the application is healthy inside the AKS cluster before exposing it to the internet.

### Check Pods
```bash
kubectl get pods -n default -o wide
```
✅ All app Pods should be in `Running` state.  

### Check Service
```bash
kubectl get svc -n default
```
✅ Service should be `ClusterIP` type with correct port mapping (e.g., `80/TCP`).  

### Check Ingress Controller
```bash
kubectl get pods -n ingress-nginx -o wide
```
✅ NGINX ingress-controller Pods should be `Running`.  

### Check Ingress Resource
```bash
kubectl get ingress -n default
```
✅ Host (`skhan.tech`) should map to your app Service.  

### Curl inside cluster
```bash
kubectl run curlpod --rm -it --image=curlimages/curl -- sh
curl -vk http://<service-name>:80
```
✅ Should return app response.  

---

## 2️⃣ Validate Application from Internet

These checks confirm that the app is publicly accessible.

### DNS Resolution
```bash
nslookup skhan.tech
```
✅ Should resolve to the **Azure LB Public IP**.  

### Check LoadBalancer External IP
```bash
kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller
```
✅ `.status.loadBalancer.ingress[0].ip` should match DNS.  

### TLS Certificate Validation
```bash
curl -vk https://skhan.tech
```
✅ Certificate should be valid (CN = `skhan.tech`, Issuer = `ZeroSSL`, chain includes `ca_bundle.crt`).  

### Application Response
```bash
curl -vkL https://skhan.tech
```
✅ Should return HTTP `200 OK` with your app response.  

---

## 3️⃣ Traffic Flow from Internet to AKS

Below diagram explains how a request flows through each hop:

```
+-------------+
|   Browser   |
|  curl/wget  |
+------+------+ 
       |
       v
+-------------+      Public IP (Azure Load Balancer)
|   Internet  |----------------------------+
+-------------+                            |
                                           v
                                 +-----------------------+
                                 | Azure Load Balancer   |
                                 | (probes: /healthz     |
                                 |  on port 10254)       |
                                 +----------+------------+
                                            |
                                            v
                                +------------------------+
                                | NGINX Ingress Service  |
                                | (Type: LoadBalancer)   |
                                +-----------+------------+
                                            |
                                            v
                                +------------------------+
                                | NGINX Ingress Pod(s)   |
                                | - TLS termination      |
                                | - Host/path routing    |
                                +-----------+------------+
                                            |
                                            v
                                +------------------------+
                                |   Backend Service      |
                                | (ClusterIP Service)    |
                                +-----------+------------+
                                            |
                                            v
                                +------------------------+
                                |   App Pod(s)           |
                                | (skhan-app container)  |
                                +------------------------+
```

### Step-by-step explanation:
1. **Client** → Resolves `skhan.tech` → Azure LB public IP.  
2. **Azure LB** → Health probes `/healthz:10254`, forwards traffic.  
3. **Ingress Service** → Exposes NGINX ingress via LoadBalancer.  
4. **Ingress Pod** → Terminates TLS (`skhan-tls` secret), routes based on host/path.  
5. **Backend Service** → ClusterIP service balancing across app Pods.  
6. **App Pods** → Application responds with `200 OK`.  

---
