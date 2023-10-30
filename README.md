# tg-plot

generate a visual plot from a list of messages in telegram channel.

## run

requirements:
- **docker**
- **docker compose**

```
docker compose up
```

go to http://localhost:8000

## development

```
# run this every time Pipfile is altered
pipenv install --dev && pipenv requirements > requirements.txt

# run with live code reloading
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## License

MIT