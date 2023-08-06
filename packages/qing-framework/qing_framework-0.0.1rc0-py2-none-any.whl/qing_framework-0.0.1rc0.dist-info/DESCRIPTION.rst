Framework for building Data pipelines that scales.

Installation
====
```
pip install qing-framework
```

Usage
=====
Build your first worker
-----------------------
``` python
# normalizer_worker.py
from qing_framework import QingWorker
from qing_framework import QingMessage as QM

class Normalizer(QingWorker):
    def process(self, qs):
        #do your magic
        formatted_messages = []
        # messages from queue named 'dummy' are loaded for you automagically inside the qs variable.
        while message in qs['dummy']:
            # Each QingMessage has a payload and now you can create your own after modifying!
            formatted_message = QM( payload="formatted: " + message.payload )
            formatted_messages.append(formatted_message) 
        #returned messages are automatically writted to output queue!
        return formatted_messages
```

``` python
# normalizer_manifest.py
# This file describes worker's responsibility and dependencies.
{
	'name':'normalizer',
	'author': 'AlSayed Gamal',
	'version': '0.0.1',
	'description': 'normalizes messages into proper format!',
	'in-queues': ['dummy'],
	'out-queues': ['normalized'],
	'activity-rate': '5000',
	'class': 'Normalizer'
}
```
Run worker using CLI
--------------------
You can start qing as a server and use qing's CLI to run and scale the worker
```bash
#queen cli and UI for qing framework.
qing --help # just in case you needed help.
qingd # qing deamon, you will need sudo permission
qing run Normalizer # run a specific worker
qing kill Normalizer --job-id=123 #kill specific worker job
```

Monitor the data-pipeline using Web-UI
--------------------------------------
```bash
qing --webserver --port=8910 # you can view data pipelines, queues, jobs and workers.
```

