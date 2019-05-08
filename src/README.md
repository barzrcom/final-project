# Final Project
## ML Server
### Building
NOTE: Need to be at the location of 'src/' (The location of the 'Dockerfile')
```bash
docker build -t gag_ml:latest .
``` 
### Run it
```bash
docker run --name GAG_ML -d -p 5000:5000 gag_ml:latest
```
NOTICE: Only one instance of the server could run, to stop the existing one execute:
```bash
docker rm -f GAG_ML
```
