### ids-http
Build image

    docker build -t ids:1-http .
    

### ids-tls
Let's assume: 
- certificate is available under this path: `/home/opc/ids-certs/cert.pem` 
- certificate key is available under this path: `/home/opc/ids-certs/key.pem` 

    docker build -t ids:1-tls .
    docker run -d -p 5443:5000 -e "NODE_NAME=ids-1" -v /home/opc/ids-certs:/certs  --name ids-1 ids:1-tls
