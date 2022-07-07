all: secrets/ca_key

secrets/ca_key: 
	python3 ./genkey.py 

clean:
	rm -rf secrets 
