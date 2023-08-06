# vmtools
misc tools to make working with python virtualenv easier

vm_root_grabber
Get the current time and return a dictionary with the current time available in various formats
I use it to be able to find the local_settings.pys file and import all variable from that file.

```
import vmtools
vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *
```

get_time
Get the current time and return a dictionary with the current time available in various formats

