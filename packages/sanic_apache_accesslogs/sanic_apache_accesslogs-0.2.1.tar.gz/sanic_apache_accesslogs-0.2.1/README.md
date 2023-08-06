# Sanic Apache Access Logs

Sanic Plugin to log access logs in common or combined format

## How to use


```python
from sanic import Sanic
from sanic.response import json
from sanic_apache_accesslogs import AccessLogPlugin


app = Sanic(__name__, configure_logging=False)

AccessLogPlugin(app)


@app.route('/', methods=['GET'])
async def hello(request):
    return json({'hello': 'world'})


if __name__ == '__main__':
    app.run(host='localhost', port=5000, access_log=False)
```


## Common or Combined?


For choosing the format set the environment variable `ACCESSLOG_USE_COMBINED` to choose combined over common.


## TODO(s)

* Use Sanic configuration context to choose between the logging format.


## Contact

Arnulfo Solis
arnulfojr94@gmail.com
