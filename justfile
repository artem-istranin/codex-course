image := "wheel-winner"
container := "wheel-winner"
port := "8080"
container_port := "8000"

build:
    docker build -t {{image}} .

run:
    docker run --rm --name {{container}} -p {{port}}:{{container_port}} {{image}}

inspect:
    docker image inspect {{image}}

smoke:
    curl --fail --silent --show-error http://127.0.0.1:{{port}}/health
