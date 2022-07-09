all: secrets/ca_key

secrets/ca_key: 
	python3 ./genkey.py 

release:
	helm package -d docs cloud-server
	helm repo index docs

clean:
	rm -rf secrets 
