# Final Project
## ML Server
### Building
NOTE: Need to be at the location of 'src/ml' (The location of the 'Dockerfile')
```bash
docker build -t gag_ml:latest .
``` 
### Run it
```bash
docker run -h gag_ml -d -p 5000:5000 gag_ml:latest
```