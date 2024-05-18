build:
  docker build -t sense .

run: build
  docker run --rm --env-file=./.env sense