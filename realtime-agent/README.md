## How-to, this model based on [evolution-strategy](https://github.com/huseinzol05/Stock-Prediction-Models/tree/master/agent)

1. You can check [realtime-evolution-strategy.ipynb](realtime-evolution-strategy.ipynb) for to train an evolution strategy to do realtime trading.

I trained the model to learn trading on different stocks,

```python
['TWTR.csv',
 'GOOG.csv',
 'FB.csv',
 'LB.csv',
 'MTDR.csv',
 'CPRT.csv',
 'FSV.csv',
 'TSLA.csv',
 'SINA.csv',
 'GWR.csv']
```

You might want to add more to cover more stochastic patterns.

2. Install the runtime dependencies from the repository root,

```bash
python -m pip install -r ..\requirements.txt
```

3. Run [app.py](app.py) to serve the checkpoint model using Waitress,

```bash
python app.py
```

From PowerShell, you can also use the helper scripts:

```powershell
.\realtime-agent\start-server.ps1
.\realtime-agent\stop-server.ps1
```

Containerized startup from the repository root:

```powershell
docker compose up --build
```

```text
INFO app Starting waitress server host=0.0.0.0 port=8005 threads=8
```

4. You can check requests example in [request.ipynb](request.ipynb) to get a kickstart.

```bash
curl http://localhost:8005/trade?data=[13.1, 13407500]
```

You can also send JSON with `POST /trade`:

```bash
curl -X POST http://localhost:8005/trade ^
  -H "Content-Type: application/json" ^
  -d "{\"data\": [13.1, 13407500]}"
```

Inspect runtime metadata:

```bash
curl http://localhost:8005/metadata
```

Or use the included local client:

```bash
python client.py health
python client.py trade --close 13.1 --volume 13407500
```

```python
{'action': 'sell', 'balance': 971.1199990000001, 'investment': '10.224268 %', 'status': 'sell 1 unit, price 16.709999', 'timestamp': '2019-05-26 01:12:10.370206'}
{'action': 'nothing', 'balance': 971.1199990000001, 'status': 'do nothing', 'timestamp': '2019-05-26 01:12:10.376245'}
{'action': 'sell', 'balance': 987.7799990000001, 'investment': '11.066667 %', 'status': 'sell 1 unit, price 16.660000', 'timestamp': '2019-05-26 01:12:10.382282'}
{'action': 'nothing', 'balance': 987.7799990000001, 'status': 'do nothing', 'timestamp': '2019-05-26 01:12:10.388330'}
{'action': 'nothing', 'balance': 987.7799990000001, 'status': 'do nothing', 'timestamp': '2019-05-26 01:12:10.394324'}
{'action': 'sell', 'balance': 1006.1299990000001, 'investment': '18.387097 %', 'status': 'sell 1 unit, price 18.350000', 'timestamp': '2019-05-26 01:12:10.400104'}
{'action': 'nothing', 'balance': 1006.1299990000001, 'status': 'do nothing', 'timestamp': '2019-05-26 01:12:10.405804'}
{'action': 'nothing', 'balance': 1006.1299990000001, 'status': 'do nothing', 'timestamp': '2019-05-26 01:12:10.411531'}
```

## Notes

1. You can use this code to integrate with realtime socket, or any APIs you wanted, imagination is your limit now.
2. `app.py` now resolves `model.pkl` and the CSV dataset relative to its own folder, so it works when launched from either the repo root or `realtime-agent/`.
3. The default dataset is `TWTR.csv`, and you can override it with `REALTIME_AGENT_DATA_PATH`.
4. Logs are written to `realtime-agent/logs/realtime-agent.log` and controlled by `REALTIME_AGENT_LOG_LEVEL`.
5. The service now runs behind Waitress instead of Flask's development server.
