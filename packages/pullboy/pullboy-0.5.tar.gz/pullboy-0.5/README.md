PullBoy
=======

Pullboy is a VERY simple server that listens for incoming connections and deploys projects according to a predefined script.

Steps
-----

First we install pullboy. `pip install pullboy` or the preferred one `pipenv install pullboy`. Second we write the deploy config file. An example would be:

```yaml
pullboy:
    workdir: '~/pullboy'
    script:
        - git pull origin master
        - make
    token: 'thisisnosecret'
    active: true  # This is optional. Default is assumed to be true
```


I sometimes use it to update my servers where the pullboy config is as below. The important thing is that all commands end in a reasonable time. The `fuser` command kills the process using 8000 as a tcp port (which is the previous instance of the server.

```yaml
pullboyserver:
    workdir: '~/myserver'
    script:
        - git pull origin master
        - make
        - fuser -k 8000/tcp
        - pipenv run python myserver.py &
    token: 'this is no secret'
    active: true
```

Now we run pullboy with the following command `pullboy config.yaml`.

That's it.

Notes
-----

To make pullboy deploy something all you need to do is hit `https://wherever.pullboy.is.running.com:8764/deploy` with the items `project` and `token` in the POST body. For this activity **HTTPS is recommended**.

Tokens are meant to be kept a secret otherwise anyone with access to this URL can deploy the code (we don't want it to be that simple do we?).  An example cURL command to deploy the project shown in the config above would be:

```bash
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/deploy`
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/cleanupdatabase`
curl -X POST -F project=pullboy -F token=thisisnosecret https://wherever.pullboy.is.running.com:8764/pullboy/deploy`
```

The url does not matter, whatever URL you access, pullboy will be ready to work. This makes it easy to use with a reverse proxy like Nginx where you can forward a url like `/pullboy/deployments/ci` and `/pullboy/deployments/manual` to Pullboy. The Nginx logs can act as *logs* for deployments.

[Let's Encrypt](https://letsencrypt.org/) is the recommended way to obtain HTTPS but in case you are using your laptop for something, [ngrok](https://ngrok.com/) is a neat way to get HTTPS.
