![activatelease](https://user-images.githubusercontent.com/2152766/117956343-db98b980-b310-11eb-9bdf-80ba6fc949f7.gif)

Congratulations on your purchase of a floating licence for **Ragdoll Dynamics**!

## Overview

This page will help you get set-up with a licence server, on-premise, and instruct Ragdoll to "lease" a licence from it. The server itself can run on any machine and any platform, including Windows, Linux and MacOS, so long as it is accessible from the machine running Ragdoll.

**Windows, Linux and MacOS**

The server can run on a different operating system than your workstations. For example, a common scenario is having the server running on Linux and workstations run on a combination of Windows, MacOS and Linux.

On each platform, the procedure is the same.

1. Download the server software
2. Optionally edit the configuration file
3. Activate the server with your `Product Key`
4. Start it up

The server will need to remain running in order for Ragdoll to lease licences.

<br>

## Linux

Here's a typical series of commands for an x64 system, look inside [the .zip](https://files.ragdolldynamics.com/api/public/dl/hAlavAOP/TurboFloat-Server-Linux.zip) for alternative Linux-based platforms.

!!! hint "Requirements"
    Make sure you have `unzip` and `wget` at the ready, or use alternatives like `curl` and `tar` at your own leisure.

```bash
mkdir turbofloat
cd turbofloat
wget https://files.ragdolldynamics.com/api/public/dl/hAlavAOP/TurboFloat-Server-Linux.zip
wget https://files.ragdolldynamics.com/api/public/dl/6lMDDMdn/TurboActivate.dat
unzip TurboFloat-Server-Linux.zip
mv bin-linux/x64/turbofloatserver ./
chmod +x turbofloatserver
./turbofloatserver -a="YOUR-SERIAL-NUMBER"
./turbofloatserver -x
# Floating license server for Ragdoll Dynamics (TFS v4.4.4.0)
```

> You can optionally pass `-silent` after `-x` for less verbosity.

??? question "No internet?"
    The licence server can be activated offline.

    - See [Can I activate my server offline?](#can-i-activate-my-server-offline)

From here, you'll likely want `turbofloatserver -x` called automatically on reboot, such that Ragdoll and Maya can lease licences from it. The exact procedure varies between Linux distributions and company preferences, so I won't go into details here except to say that [systemd](https://www.linux.com/training-tutorials/understanding-and-using-systemd/) is a common option.

**More Details**

- [Installation Options](https://wyday.com/limelm/help/turbofloat-server/#install)
- [Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

## Windows

Here's what you need to do in order to run the licence server on the Windows platform.

<br>

### Download

- [`TurboFloat-Server-Windows.zip`](https://files.ragdolldynamics.com/api/public/dl/PdFO00Vv/TurboFloat-Server-Windows.zip)

Inside of this file you will find this.

![image](https://user-images.githubusercontent.com/2152766/117801629-73809f80-b24c-11eb-83ee-c5b548a8c2f0.png)

Edit the `.xml` file with a `port` you would like to use.

!!! note "Port number"
    Make note of this port number as you will need it later when connecting to it from Maya.

!!! note "64-bit Server"
    If you need a 32-bit version of the server, find the appropriate `TurboFloat` binaries here.

    - https://wyday.com/download/


<br>

### Activate

Next we'll need to activate the server. Open a `cmd.exe` or PowerShell prompt and type in the following.

```bash
TurboFloatServer.exe -a="YOUR-SERIAL-NUMBER"
```

There should be no output from the command, unless there's a problem.

??? question "No internet?"
    The licence server can be activated offline.

    - See [Can I activate my server offline?](#can-i-activate-my-server-offline)

Now you're ready to launch the server!

<br>

### Start

This next command will launch the server.

```bash
TurboFloatServer.exe -x
# Floating license server for Ragdoll Dynamics (TFS v4.4.3.0)
```

!!! hint "Test"
    This is a good place to test Ragdoll from within Maya, so [scroll to the Maya section](#maya), test it out and then come back here to finish things up.

All good? Great.

**Optional**

At this point, you can optionally have the server restart itself and run in the background by installing it as a "service".

```bash
TurboFloatServer.exe -i
# 2021-05-12, 07:47:26 <error>: OpenSCManager failed (5)
```

To do that, you'll need to launch PowerShell/cmd as **Administrator**.

```bash
# As Administrator
TurboFloatServer.exe -i
# 2021-05-12, 07:48:40 <notification>: Service installed successfully.
```

From here you can try launching Ragdoll Dynamics in Maya to see whether it manages to successfully lease a licence.

**More Details**

- [Installation Options](https://wyday.com/limelm/help/turbofloat-server/#install)
- [Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

## Maya

With a licence server running, your next step is having Ragdoll connect to it.

On each platform, the procedure is the same.

- Set `RAGDOLL_FLOATING`
- Load plug-in

**Example**

```py
# From Python
os.environ["RAGDOLL_FLOATING"] = "127.0.0.1:13"
cmds.loadPlugin("ragdoll")
```

```bash
# From an environment like bash
export RAGDOLL_FLOATING=127.0.0.1:13
maya
```

The format of `RAGDOLL_FLOATING` is `<ip-address>:<port-number>`.

<br>

**Everything ok?**

??? bug "Failed to initialise floating licence"
    If this message appears in your Script Editor upon loading the plug-in, take a closer look at your Output Window on Windows or terminal on Unix.

    ```py
    # Error: ragdoll._install_floating() - Failed to initialise floating licence, error code '1' # 
    ```

??? bug "Could not load ragdollfloat.dll"
    Windows users may experience this issue, which indicates a broken install. In your distribution, you should have seen both a `ragdoll.mll` and `ragdollfloat.dll`. Make sure this file exists, else [contact us](mailto:licencing@ragdolldynamics.com) and we'll help you sort it.

<br>

## Python

Just like with a node-locked licence, you can control the leasing of licences via Python.

```py
from ragdoll import licence

# Activate this machine
licence.request_lease()

# Deactivate this machine
licence.drop_lease()
```

<br>

## Troubleshooting

Let's have a look at a few common errors and how to solve them.

<br>

### Failed to Save Activation Request

This can happen when attempting to generate an activation request for offline activation.

```bash
./turbofloatserver -a="KWVT-U5RS-..." -areq="/bad/path/request.xml"
# <error>: Failed to save the activation request file.
# <error>: Error code 0x1. Contact support or your system administrator.
```

The path given, in this case `/bad/path/request.xml` might not be writable. Try a different path.

<br>

### Failed to Load Product Details

This can happen when attempting to activate a floating licence

```bash
./turbofloatserver -a="KWVT-U5RS-..."
# <error>: Failed to load the product details file.
# <error>: Failed to load the settings.
```

The `turbofloatserver` executable wasn't able to find the `TurboActivate.dat` file. This file should reside in the same folder as `turbofloatserver` and can be downloaded from here.

- https://files.ragdolldynamics.com/api/public/dl/6lMDDMdn/TurboActivate.dat

<br>

## FAQ

Let's cover some common scenarios.

<br>

### How can I test connectivity between my machines?

To test whether machine A is accessible from machine B, try `ping`.

```bash
ping 10.0.0.13
# Reply from 10.0.0.13: bytes=32 time=1ms TTL=117
```

<br>

### Can I limit the internet access of my licence server?

If you're in a secure network, you may want to limit the licence server to the least amount of external access. You can do so by "whitelisting" it in your firewall, using this URL and port number.

- url: `https://wyday.com`
- port: `443`

More details here: https://wyday.com/limelm/help/turbofloat-server/

<br>

### Can I activate my server offline?

Lifetime licences, yes. Monthly licences, no.

Like node-locked licences, the floating licence server can be activated without an internet connection to the machine running the server.

The procedure is the same on each platform.

1. Generate an activation request from the computer running the licence server
2. Go to https://ragdolldynamics.com/offline
3. Activate using the response from the same computer

Here's how to generate the request.

```bash
./turbofloatserver -areq="~/ActivationRequest.xml" -a="YOUR-SERIAL-NUMBER" 
```

And here's how to apply the response.

```bash
./turbofloatserver -aresp="~/ActivationResponse.xml" -a
```

<br>

### What happens when my server is offline?

Leasing will attempt to connect for about 2 seconds until giving up. During that time, Maya may appear frozen.

<br>

### What happens when my server *goes* offline?

Leasing is re-done once every 30 minutes.

30 minutes is the default value (see below), which means that if the server goes down whilst an artist is using it, the solver will be disabled within 30 minutes.

The duration can be adjusted, however it is a balance since the time is also how long it takes for the server to *free* a lease as a result of a Maya crash.

- See [What happens to a lease when Maya crashes?](#what-happens-to-a-lease-when-maya-crashes)

<br>

### Can I change the port used by the server?

Yes.

The default port is `13` and can be edited via the `TurboFloatServer-config.xml` file residing in the same directory as the server executable.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <bind port="13"/>
    ...
</config>
```

- [More Configuration Options](https://wyday.com/limelm/help/turbofloat-server/#config)

<br>

### Can I move my licence server to a different machine?

Yes.

To move a licence, you can deactivate it and then activate it again someplace else.

```bash
TurboFloatServer -deact
```

This will deactivate the server. The same can be done if your licence server is offline, by passing a filename to the command.

```bash
TurboFloatServer -deact="deactivation_request.xml"
```

Open this file and paste the contents of it into the offline deactivation wizard here.

- https://ragdolldynamics.com/offline

<br>

### What if I have multiple serial numbers?

Complete, Unlimited and Batch have their own serial numbers and each serial number needs its own server.

- Each server needs to be a physical machine, but can under certain circumstances be allowed to run within a virtual machine; [contact us](mailto:licencing@ragdolldynamics.com) if this is you.
- Each server needs their own unique address. If they run on the same machine, you can assign a unique port number (see [above](#can-i-change-the-port-used-by-the-server)).

From there, provide each of your clients with the full server address to the pool it should lease licences from.

For example.

```bash
# Render farm
RAGDOLL_FLOATING=10.0.0.4:601

# Artist workstations
RAGDOLL_FLOATING=10.0.0.4:602
```

<br>

### Can I disable the splash screen?

Yes.

Consumers of floating licences generally won't need to manage licenses themselves, and so the startup dialog can be avoided altogether for a smoother experience when inside of Maya.

```bash
export RAGDOLL_NO_STARTUP_DIALOG=1
maya
```

- See [Environment Variables](/api/#environment-variables) for details

<br>

### What happens to a lease when Maya crashes?

A lease is automatically dropped upon unloading the plug-in or shutting down Maya. In the event of a Maya crash, a lease will automatically drop after 30 minutes per default.

The time can be edited via the configuration file; a lower time means more compute and file resources are consumed on the server, the lowest value is 30 seconds.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <lease length="30"/><!-- seconds -->
    ...
</config>
```

<br>

### Can I fall back to a node-locked licence?

Yes.

Remove the `RAGDOLL_FLOATING` environment variable and reload the plug-in or restart Maya to attempt activation of a node-locked licence.

<br>

### Can I activate my server on a Virtual Machine?

No.

The server cannot distinguish between two virtual machines which would make it possible to activate an endless amount of them with their own duplicate pools of licences.

Although the *server* cannot run on a VM, clients *can*. E.g. running Docker for testing in a continous-integration environment or automation for simulation baking or rendering etc.

<br>

### Can I monitor my licence server?

Yes.

With a logging level set to "notification", you'll get real-time output from the server whenever a lease is requested and dropped, including..

1. Time of event
1. Expiry time
1. IP
1. Username
1. PID (Process ID)

The expiry is when the lease will be renewed. Normally not something you need to worry about, unless Maya crashes. This is then the time it'll take the server to realise the lease has been freed.

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    ...
    <log file="tfs-log.txt" level="notification"/>
    ...
</config>
```

```bash
2021-05-12, 11:58:47 <notification>: New connection from IP: ::ffff:127.0.0.1
2021-05-12, 11:58:47 <notification>: New lease assigned (marcus, 1, IP=::ffff:127.0.0.1, PID=14328). Expires: 2021-05-12 11:28:47 (in UTC). Used / Total leases: 1 / 1
2021-05-12, 11:58:51 <notification>: New connection from IP: ::ffff:127.0.0.1
2021-05-12, 11:58:51 <notification>: Lease was released by client (marcus, 1, IP=::ffff:127.0.0.1, PID=14328). Used / Total leases: 0 / 1
```

A Python and web interface to this will be part of a future release, but the formatting can be relied upon for building your own monitoring mechanism.

<br>

### What does the server say when a lease request is rejected?

With `level="notification"` it'll say this.

```bash
2021-05-16, 14:52:50 <notification>: License lease request rejected because no more free slots, numTotalLics=9, pkey=YOUR-SERIAL-NUMBER
```
