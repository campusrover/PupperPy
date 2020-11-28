# cerbaris-client (frontend)

## Set up for development

1. Get `.env` files and move to correct places

2. `cd` into `web/cerbaris-client` directory

3. `npm install`

## Run Locally

1. `npm run serve`

2. Go to `localhost:8080` in browser. (If port 8080 is already being used, it will automatically be served on another port - check terminal output.)

3. Open another terminal window and `cd` into `pupperpy` directory

4. `python3 control_loop.py`

5. Don't forget to ctrl-C the Python script when you're finished

## Deploy
```
npm run deploy
```

## Compile and minify for production
```
npm run build
```

## Lint and fix files
```
npm run lint
```

## Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
