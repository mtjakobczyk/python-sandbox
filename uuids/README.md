### ids-http
:wrench: UUID API over HTTP  
Build and run container:

    docker build -t ids:1-http .
    docker run -d -p 5080:5000 -e "NODE_NAME=ids-1" ids-1 ids:1-http
    

### ids-tls
:wrench: UUID API over HTTPS  
Let's assume certificate `cert.pem` and its key `key.pem` are present under this path: `/home/opc/ids-certs/`  
Build and run container:


    cd ids-tls/
    docker build -t ids:1-tls . 
    docker run -d -p 5443:5000 -e "NODE_NAME=ids-2" -v /home/opc/ids-certs:/certs  --name ids-2 ids:1-tls

