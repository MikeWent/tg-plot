# tg-plot

generate a visual plot from a list of messages in telegram channel.

## Install on your server

requirements:
- **docker** on server
- **docker compose** on PC


1. build and run tg-plot
    ```
    export DOCKER_HOST=ssh://server
    docker compose up --build --detach
    ```
2. go to `http://server:8000`

## development

```
pipenv install --dev && pipenv requirements > requirements.txt

docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## License

MIT