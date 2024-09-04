# Setup

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


# Environment Variables [Optional]

## Debug

Setting `DEBUG` to `True` will enable the FastHtml auto-reload and live reloading the browser on changes.

```
export DEBUG=True
```

## PocketBase URL

By default the PocketBase instance will be access at `http://localhost:8090`. If you want to change this, you can set the `PB_BASE_URL` environment variable.

```
export PB_BASE_URL=https://my-pb-backend.pockethost.io
```

# Run

 ```
 python app/main.py
 ```

 1. Navigate to http://localhost:5001
 2. You should be redirected to /login
 3. Login with one of your users that exist in your PocketBase users collection
 

 # Customize

Customize for your own use case. By default this example is authenticating with the `users` collection in PocketBase. You can change this to authenticate with a different collection, as well as the data that is stored in the session that represent the authenticated user.
