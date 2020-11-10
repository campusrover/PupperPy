# How to run

1. Get `.env` files and move to correct places

2. `cd` into `cerbaris-web-frontend` directory

3. `npm install`

3. `npm run serve`

4. Go to `localhost:8080` in browser. (If port 8080 is already being used, it will automatically be served on another port - check terminal output.)

5. Open another terminal window and `cd` into `PupperPy` directory

6. `python test_control_loop.py`

7. Don't forget to ctrl-C the Python script when you're finished

# Notes

* It doesn't remove rows, only adds and updates existing ones

# TODO

* Test out camera

* Display visual using velocities/yaw and goal pose

* Remove and hide rows

* Sort

* Track data