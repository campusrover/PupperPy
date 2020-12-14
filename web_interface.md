---
layout: template
---
# [Web Interface](https://cerbaris.netlify.app/)

## Overview

The web interface displays data about the robot's current state in real time. This includes data from the object sensors and IMU, as well as the bounding box and current behavior of the robot. The goal of the web interface was to easily visualize what data the robot was receiving from the control code and sensors for debugging purposes. In addition, because of lab and campus restrictions, it was sometimes easier to watch the robot remotely from the web interface rather than go to the robotics lab.

## Software architecture

![architecture](/figures/web_architecture.png)

The two biggest challenges in coding the web interface were:

1. realtime communication between the website and an external script

1. creating visual diagrams based on received data

The first challenge was solved by using an external service called Pusher, while the second required using a mix of different JavaScript libraries - mainly Vue.js, paper.js, and JointJS.

### Real-time updates

To push updates to the web interface in real time, we used [Pusher](https://pusher.com/). With Pusher, we can send data directly from the python code to the web interface in two steps. First, we trigger an event from python:

```python
# PusherInterface.py
self.client.trigger('sensor_data', 'new', {
  'timestamp': message['time'],
  'yaw': message['yaw'],
  # ... etc
}
```

Using the app-specific keys in the `.env` file, this triggers the `new` event on the `sensor_data` channel with the given data. In the second step, this data is received on the JavaScript side:

```js
// SensorPanel.vue
const pusher = new Pusher(process.env.VUE_APP_PUSHER_KEY, {
  cluster: process.env.VUE_APP_PUSHER_CLUSTER,
});

const channel = pusher.subscribe('sensor_data');
channel.bind('new', this.update);
```

Here, the sensor panel is subscribing to any messages on the `new` event of the `sensor_data` channel. When a message is received, the `update` function is called, which updates the diagrams and data tables with the new information.

### Vue.js

We used a frontend framework called [Vue.js](https://vuejs.org/v2/api/) for the web interface. Vue is component-based, so it works well for something like the CERBARIS Dashboard, which needed to have several panels displaying different types of information. Each component defines a visual subsection of the interface:

![component diagram](/figures/web_components.png)

By separating the web interface into components early on, we were able to enforce modularity into the frontend code. Vue also enforces a certain style of communication between components, moving from parent to child.

### Sensor and bounding box diagrams

The diagrams on the main page of the web interface were created using [paper.js](http://paperjs.org/about/), which is a library that builds on the [JavaScript Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API). Using paper.js, we created diagrams out of simple shapes that  change color, rotation, scale, or position depending on the current state of the robot. These are discussed in much greater detail in the following sections:

* [Sensor diagram](#sensor-diagram)
* [Map diagram](#map-diagram)
* [Bounding box diagram](#bounding-box-diagram)

### Behavior tree diagram

![behavior tree](/figures/web_behavior_tree.png)

One goal of the project was to be able to describe and modify the behavior of the robot using behavior trees. To reflect this on the web interface, we developed an interactive graph using a JavaScript library called [JointJS](https://resources.jointjs.com/docs/jointjs/v3.2/joint.html).

With JointJS, the canvas is split roughly into three parts: elements, or nodes of the graph; links, or edges that connect nodes; and blank, or empty parts of the canvas. With this framework, we built a tokenizer and parser to convert a text file representing behavior tree into a JointJS graph. Then, using pointer and key events, we made the graph interactive, so that a user can create, delete, and edit different parts of the graph.

### Styling

We used a Vue wrapper around the CSS framework [Bootstrap](https://bootstrap-vue.org/) to quickly style the web interface. Bootstrap has built-in HTML elements, such as Cards, that we used. It also uses HTML classes to determine the styles applied to an element, which makes styling responsively much easier.

```html
<!-- SensorPanel.vue -->
<b-card-body class="panel-body d-flex justify-content-center flex-wrap flex-lg-nowrap p-2">
  <sensor-diagram class="m-1" :sensor-data="sensorData" :yaw="yaw" :timestamp="timestamp"></sensor-diagram>
  <map-diagram class="m-1" :pos-data="posData" :timestamp="timestamp"></map-diagram>
  <b-table hover sticky-header small class="m-1 flex-fill" style="max-height: 250px" :items="dataTable"></b-table>
</b-card-body>
```

In this code snippet, we use the BootstrapVue element `b-card`. The `b-card-body` element has classes `d-flex`, `flex-wrap`, and `flex-lg-nowrap`. This means that the element will be displayed using flex, and will wrap for screens smaller than large (width 1200 pixels and up).

## Code design

Here, we explain the most interesting parts of the web interface code.

### PusherInterface.py

The data is separated into four channels within the `send` method of `PusherInterface.py`:

* `sensor_data`: object sensor data and IMU (position, velocity, and acceleration) data
* `vision_data`: bounding box size, position, label, and confidence
* `state_data`: state name and velocity/yaw commands
* `tree_data`: behavior tree and active node

We chose to separate the data into these four channels, rather than combining them into one and separating the data in the frontend. This was to allow the panels to update independently of each other; we wanted the web interface to eventually be able to accommodate updating different sections of the data at different times and frequencies. In addition, the Pusher documentation suggests separating by channels rather than events or within the frontend for performance purposes. 

### Sensor diagram

![sensor diagram](/figures/sensordiagram.gif)

The sensor diagram receives the object sensor data and the robot's yaw. It visualizes the object sensor data using three rectangles which change color depending on whether the corresponding object sensor is currently sensing something. The three rectangles are initialized as follows:

```js
// SensorDiagram.vue
let sensor_w = 10
let sensor_h = 2 * sensor_w
this.leftSensor = new Path.Rectangle({
  point: [10, 10],
  size: [sensor_w, sensor_h],
  fillColor: 'rgba(15, 234, 0)',
  opacity: 1,
})
// ... etc.
```

Their colors are then updated by calling the `updateRangeSensor` method.

```js
// SensorDiagram.vue
updateRangeSensor(sensor, value) {
  if (value) {
    sensor.fillColor = 'red'
  } else {
    sensor.fillColor = 'rgba(15, 234, 0)'
  }
}
```

The sensor diagram visualizes the robot's yaw as a rotating rectangle with an arrow. First, radial axes are drawn to give the user an intuition for the yaw value.

```js
// SensorDiagram.vue
let num_axes = 8
for (let i = 0; i < num_axes; i++) {
  let axis = new Path.Line({
    from: [this.width/2, this.height/2],
    to: [this.width/2, -this.height],
    strokeColor: 'black',
    opacity: .2
  })
  axis.rotate(i * 360 / num_axes, new Point(this.width/2, this.height/2))
}
```

Then, the robot (gray box) and arrow are drawn and grouped.

```js
// SensorDiagram.vue
// forward arrow
let arrow_w = 10
let arrow_h = 10
let forward_arrow = new Path.Line({
  from: [this.width/2, this.height/2],
  to: [this.width/2, 0],
  strokeColor: 'black',
})
forward_arrow.add({point: [this.width/2 - arrow_w/2, arrow_h]})
forward_arrow.add({point: [this.width/2, 0]})
forward_arrow.add({point: [this.width/2 + arrow_w/2, arrow_h]})
// robot body
let robot_w = 60
let robot_h = 1.5 * robot_w
let robot = new Path.Rectangle({
  point: [(this.width - robot_w) / 2, (this.height - robot_h) / 2],
  size: [robot_w, robot_h],
  fillColor: 'black',
  opacity: .5,
})
// robot group
this.robotGroup = new Group([forward_arrow, robot])
```

Grouping the arrow and robot body makes changing their rotation very easy.

```js
// SensorDiagram.vue
updateYaw() {
  if (this.yaw == null) return
  this.robotGroup.rotate(-this.robotGroup.rotation, new Point(this.width/2, this.height/2))
  this.robotGroup.rotate(this.yaw, new Point(this.width/2, this.height/2))
}
```

### Map diagram

![map diagram](/figures/mapdiagram.gif)

The most difficult part of drawing the map diagram was making sure that the robot's position could not go out of the diagram's bounds. To do this, we implemented an automatic scaling mechanism by keeping track of the bounds of the robot's current and past positions. 

```js
// MapDiagram.vue
calcMapBounds() {
  // recalculate mapBounds
  if (this.posData.x < this.mapBounds.xMin ||
    this.posData.x > this.mapBounds.xMax ||
    this.posData.y < this.mapBounds.yMin ||
    this.posData.y > this.mapBounds.yMax) {

    this.mapBounds = {
      xMin: Math.min(this.posData.x, this.mapBounds.xMin),
      xMax: Math.max(this.posData.x, this.mapBounds.xMax),
      yMin: Math.min(this.posData.y, this.mapBounds.yMin),
      yMax: Math.max(this.posData.y, this.mapBounds.yMax),
    }
  }
}
```

Then, we calculate the scale that the map needs to be to keep the robot's current and past positions within the bounds of the diagram.

```js
// MapDiagram.vue
this.scale = Math.min(this.minScale,
  (this.origin.y - this.margin) / (this.mapBounds.yMax || 1),
  (this.margin - this.origin.y) / (this.mapBounds.yMin || -1),
  (this.origin.x - this.margin) / (this.mapBounds.xMax || 1),
  (this.margin - this.origin.x) / (this.mapBounds.xMin || -1))
```

If the scale has changed, then we clear and redraw the diagram. Then we update it with the robot's new position.

```js
// MapDiagram.vue
this.reset() // clears and redraws the axes with correct scale
this.drawPath() // draws the path that the robot has taken from past to present - 1
this.drawPos() // draws the robot's current position
```

### Bounding box diagram

The bounding box diagram receives the x and y positions of the upper left corner of the bounding box, as well as its width and height. Using this information, we can clear the previous bounding box and draw the new one each time new data is received.

```js
// BoundingBoxDiagram.vue
drawBoundingBox() {
  this.scope.activate()
  if (this.bbox) {
    this.bbox.remove()
  }
  this.bbox = new Path.Rectangle({
    point: [this.bboxData.x, this.bboxData.y],
    size: [this.bboxData.w, this.bboxData.h],
    fillColor: 'red',
    opacity: .4,
    strokeColor: 'black',
  })
  console.table('bounding box delay: ' + Math.trunc(Date.now() - this.timestamp * 1000) + 'ms')
}
```

<!--- ### Behavior tree {todo}

#### Tokenizing & parsing the text file

#### Drawing the tree

#### Coding user interaction

#### Highlighting the active node --->

## What we would do next

We have several ideas for improving and further developing the web interface.

### Create a backend

Currently, the web interface is a static website, meaning that it has no backend. A backend can be used for storage and as an API. Storing all messages going through Pusher would be a huge asset to debugging both the web interface and the robot itself. It could be used to replay past messages or as a middle-man for passing behavior tree updates between the python scripts and the frontend.

### Web sockets

We are using the external Pusher service to pass information from python scripts to the frontend. Instead, we might consider coding web sockets manually. (Pusher likely uses web sockets or a similar mechanism behind-the-scenes.) This could be not just an interesting exercise, but also increase our flexibility in terms of which parts of the architecture are able to act as a *server* (sending data) or *client* (receiving data). Unfortunately, Pusher has [limited client/server libraries](https://pusher.com/docs/channels/channels_libraries/libraries), which makes communication from the frontend to the python scripts more difficult than the other way around. As an alternative to creating web sockets from scratch, future developers could research how existing Pusher libraries work and contribute to Pusher by creating a server library for JavaScript.

### Modify robot behavior from the web interface

It could be very interesting to be able to modify the robot's behavior by modifying its behavior tree on the web interface. This would require communication from the JavaScript frontend to the python scripts, either through a backend or directly using web sockets. 

### Add routes

The web interface is currently a single-page application (SPA). If we wanted to add more functionality on other routes (other than the home route), it might become necessary to convert it into a multi-page application instead, or use the Vue router to artificially create routes.

## Notes to future developers

### Pusher

Pusher requires using environment variables, which depend on the Pusher app that you will be pushing data to and receiving data from. Future developers will likely want to create their own production and development apps, which means creating two `.env` files: one in `pupperpy` that contains PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET, and PUSHER_CLUSTER; and one in `web/cerbaris-client` that contains VUE_APP_PUSHER_KEY and VUE_APP_PUSHER_CLUSTER. See the Pusher docs and [Vue docs on environment variables](https://cli.vuejs.org/guide/mode-and-env.html#environment-variables) for more information.

### Netlify

We used Netlify to deploy the frontend app; however, any static website deployment service would work. For some ideas, check [this guide from Vue](https://cli.vuejs.org/guide/deployment.html#gitlab-pages) or search for how to deploy a static website.