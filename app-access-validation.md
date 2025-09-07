# AKS Application Deployment & Validation Knowledge Base

This document explains **step-by-step validation** of the `skhan-app` deployed on AKS using Helm, including internal cluster verification and external internet accessibility checks.  

---

## **Section 1: Validate Application Inside AKS Cluster**

After deploying the application and NGINX ingress controller, it's important to verify that the application is running correctly within the cluster.

### 1.1 Verify Pods

```bash
# Check pods in default namespace
kubectl get pods -n default
kubectl get pods -n ingress-nginx
```

**Expected output:**

```
NAME                          READY   STATUS    RESTARTS   AGE
skhan-app-xxxxx                1/1     Running   0          5m
nginx-ingress-ingress-nginx-controller-xxxxx  1/1  Running 0  5h
```

- `READY` should be `1/1`  
- `STATUS` should be `Running`  

---

### 1.2 Inspect Logs of Controller Pod

```bash
POD=$(kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n ingress-nginx $POD -c controller --tail=200
```

- Look for lines confirming NGINX started and leader election succeeded.
- Ensure there are **no errors** related to SSL or configuration.

**Key logs to see:**

```
"Starting NGINX Ingress controller"
"successfully acquired lease ingress-nginx/nginx-ingress-ingress-nginx-leader"
"Backend successfully reloaded"
```

---

### 1.3 Verify Readiness & Health Probes

```bash
# Check container readiness probe
kubectl describe pod $POD -n ingress-nginx | grep Readiness -A5
```

**Expected output:**

```
Readiness:  http-get http://:10254/healthz delay=10s timeout=1s period=10s #success=1 #failure=3
```

```bash
# Test health endpoint from inside cluster
CLUSTER_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.spec.clusterIP}')
curl -v http://$CLUSTER_IP:10254/healthz
```

- Should return `200 OK`  
- Confirms that the ingress controller is healthy.

---

### 1.4 Verify Application Service

```bash
kubectl get svc -n default
```

- Confirm the `skhan-app` service exists and exposes the correct ports (`80`).  

```bash
kubectl exec -it <skhan-app-pod> -- curl http://<service-ip>:80
```

- Should return your application response or HTML content.

---

### 1.5 Verify Ingress Resources

```bash
kubectl get ingress -n default
kubectl describe ingress skhan-ingress -n default
```

- Verify `HOSTS` matches `skhan.tech`
- TLS secret `skhan-tls` is attached
- External IP is assigned

---

## **Section 2: Validate Application Accessible From Internet**

Once the app is running and ingress is healthy, verify external accessibility.

### 2.1 Check External IP

```bash
kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o wide
```

- Look for `EXTERNAL-IP`  
- This IP is used in DNS and curl tests.

---

### 2.2 DNS Resolution

```bash
nslookup skhan.tech
```

- Should resolve to the external IP of the ingress controller

---

### 2.3 Test HTTPS Connectivity

```bash
curl -vk https://skhan.tech
```

**Expected output:**

- Successful TLS handshake  
- No SSL verification errors  
- HTML response of the application (or a placeholder page if using Azure Application Gateway)

---

### 2.4 Test HTTP -> HTTPS Redirect (Optional)

```bash
curl -v http://skhan.tech
```

- Should redirect to `https://skhan.tech`  
- Confirms TLS and ingress redirect rules are configured

---

### 2.5 Verify TLS Certificate Chain

```bash
openssl s_client -connect skhan.tech:443 -showcerts
```

- Certificate chain should include:

  ```
  - skhan.tech (leaf)
  - CA bundle (intermediate)
  - Root CA
  ```

- Confirms CA bundle is correctly applied in `skhan-tls` secret.

---

### ✅ **Key Fixes Implemented During Troubleshooting**

1. **Ingress Controller Health Probe**
   '''
   kubectl get deploy -n ingress-nginx -l app.kubernetes.io/component=controller \
  -o jsonpath='{.items[0].spec.template.spec.containers[0].readinessProbe.httpGet.path}{"\n"}{.items[0].spec.template.spec.containers[0].readinessProbe.httpGet.port}{"\n"}'
   '''
   - Patched `externalTrafficPolicy: Local`
   - Correct path `/healthz` and port `10254` for Azure LB

2. **TLS Certificate**
   - Combined `skhan.tech.crt` + `ca_bundle.crt` into `fullchain.crt` for secret
   - Prevented `curl` SSL verification errors

3. **Ingress & Helm Chart**
   - Updated `values.yaml` and `ingress.yaml` to include proper `_helpers.tpl` references
   - Ensured `skhan-ingress` deployed successfully

4. **Workflow Integration**
   - CI/CD pipeline builds image, deploys app, patches ingress service, creates TLS secret, and validates ingress IP

---

This document serves as a **knowledge base for future deployments**, capturing all low-level verification steps to ensure application availability and proper ingress configuration.

