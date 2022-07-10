
release:
	helm package -d docs cloud-server
	helm repo index docs

