# a small microservice experiment

uses a server backed by "keeper" db

server need to make requests to "zoo_server"

This server should serve at localhost:5000

to start, from parent dir:

```bash
$ python3 -m zoo_keeper.flask_app.py
```

can then make curl commands to `localhost:5000`