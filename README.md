# Hue Integration

A listener which watches for changes in state of lights connected to a Philips Hue Bridge. Since the Bridge is not configured for push notifications, program relies upon polling at interval set in `settings.py` file. Upon startup, prints state of all connected lights:

```
[
    {
        "brightness": 0,
        "id": "1",
        "name": "Hue Lamp 1",
        "on": false
    },
    {
        "brightness": 254,
        "id": "2",
        "name": "Hue Lamp 2",
        "on": true
    }
]
```

Upon recognition of state change, prints `id` and changed attribute of the modified light. Once for each changed attribute:

```
{
    "id": "1",
    "on": true
}
{
    "brightness": 1,
    "id": "1"
}
```

## Install

- Install and run [Hue Bridge Simulator](https://www.npmjs.com/package/hue-simulator)
 - `sudo npm install -g hue-simulator`
 - `hue-simulator --port=8080`
 - Possible response: `hue simulator listening @ 192.168.1.9:8080`
- Download and install repository
 - `git clone https://github.com/asgaines/HueIntegration HueIntegration`
 - `cd HueIntegration`
 - `pip install -r requirements.txt`

## Run program

- With command line arguments specifying device location
 - `./hue_listen.py --ip_address=192.168.1.9 --port=8080` (address reported by `hue-simulator`)
 - or `./hue_listen.py -i 192.168.1.9 -p 8080`

- or with configuring location in settings file
 - `vim settings.py`
 - set `IP_ADDRESS` (string) and `PORT` (integer) to values for your Hue Bridge location
 - `./hue_listen.py`

- Optional: run program with stdout and logging routed to desired locations:
 - `./hue_listen.py -i 192.168.1.9 -p 8080 2> /path/to/log | tee >(josh.ai)`

## Testing

- `python -m unittest`
