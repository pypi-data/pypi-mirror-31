# logicmonitor - Python package

LogicMonitor API for Python

Simple example for https://acme.logicmonitor.com/:

	client = LogicMonitorClient('acme', 'accessIdABCDEF', 'accessKeyGHIJKLMEOP')
	device = client.get('/device/devices/66')
	print(device['id'])
