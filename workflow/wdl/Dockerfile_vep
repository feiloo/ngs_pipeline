FROM ensemblorg/ensembl-vep:release_104.3

USER root
RUN mkdir -p /var/lib/apt/lists/partial && apt-get update && apt-get install -y wget tar gzip tabix
