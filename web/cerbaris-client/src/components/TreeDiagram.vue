<template>
  <div>
    <p>Shift-click + drag to create. Alt-click to delete.</p>
    <div id="behaviorTreeDiagram"></div>
  </div>
</template>

<script>
  import * as joint from 'jointjs'
  import dagre from 'dagre'
  import graphlib from 'graphlib'

  // todo: get string from GET request to API
  // switch between normal dashboard and this using keyboard shortcut
  // make fully interactive
  const behaviorTreeString = 
`fetch ball
\tthen
\t\tunless I see a ball
\t\t\tcontinue
\t\t\t\tlook for ball
\t\tunless a ball is close enough
\t\t\tcontinue
\t\t\t\tmove towards ball
\t\twait
look for ball
\tthen
\t\tturn 432 degrees
\t\t\tunless I see an obstacle
\t\t\t\tmove forward for 5 seconds
\t\tunless I don't see an obstacle
\t\t\tcontinue
\t\t\t\tavoid obstacle

avoid obstacle
\tunless obstacle is in front for 1 second
\t\tcontinue
\t\t\tmove forward
\tunless no obstacle is in front
\t\tcontinue
\t\t\twhile
\t\t\t\tturn right
\t\t\t\tmove backward

move towards ball
\tthen
\t\tturn towards ball
\t\tunless not facing the ball
\t\t\tcontinue
\t\t\t\tmove forward
`
/*
*/

  const TreeDiagram = {
    components: {},
    props: [],
    data() {
      return {
      }
    },
    mounted() {
      this.context = document.createElement('canvas').getContext('2d')
      this.font = {
        size: 14,
        family: 'Helvetica',
      }
      this.context.font = this.font.size + 'px ' + this.font.family
      this.drawTree(this.parseTree(this.tokenize(behaviorTreeString), 0))
      this.keymap = {}
    },
    methods: {
      tokenize(text) {
        let lines = text.split('\n')
        let tokens = []
        tokens.push({tabs: -1, value: null}) // root

        lines.forEach(line => {
          if (line.trim().length === 0) {
            return
          }
          let tabs = line.lastIndexOf('\t') + 1
          let value = line.trim()
          let type = this.determineType(tabs, value)
          tokens.push({tabs, value, type})
        })
        return tokens
      },

      determineType(tabs, value) {
        if (value.startsWith('then')) {
          return 'then'
        } else if (value.startsWith('unless')) {
          return 'condition'
        } else if (tabs === 0) {
          return 'definition'
        } else {
          return 'action'
        }
      },

      parseTree(tokens, index) {
        let node = {
          value: tokens[index].value,
          type: tokens[index].type,
        }
        // base case: leaf node; no next elt or next elt's tabs <= curr elt's tabs
        if (tokens.length <= index + 1 || tokens[index + 1].tabs <= tokens[index].tabs) {
          node.children = []
          return node
        } else {
          // loop through children and call recursively
          let childIndex = index + 1
          let children = []
          while (childIndex < tokens.length && tokens[childIndex].tabs > tokens[index].tabs) {
            if (tokens[childIndex].tabs === tokens[index].tabs + 1) {
              children.push(this.parseTree(tokens, childIndex))
            }
            childIndex++
          }
          node.children = children
          return node
        }
      },

      drawTree(treeObj) {
        let graph = new joint.dia.Graph
        let paperSize = {width: window.innerWidth, height: window.innerHeight}

        let paper = new joint.dia.Paper({
          el: document.getElementById('behaviorTreeDiagram'),
          model: graph,
          width: paperSize.width,
          height: paperSize.height,
          gridSize: 1,
          interactive: true,
        })

        paper.on('element:pointerdown', (elementView, evt, x, y) => {
          if (evt.shiftKey) {
            // prevent element from being dragged
            elementView.options.interactive = false
            let width = 100
            let height = 50
            let child = new joint.shapes.standard.Rectangle({
              position: { x: x - width/2, y: y - height/2 },
              size: { width, height },
            })
            this.styleNode(child, 'new node', 'blank')
            child.addTo(graph)
            evt.data.draggedElement = child
            // create link
            let link = new joint.shapes.standard.Link()
            link.attr('line/strokeWidth', 1)
            link.source(elementView.model)
            link.target(child)
            link.addTo(graph)
          } else {
            elementView.options.interactive = true
          }

          if (evt.altKey) {
            elementView.model.remove()
          }
        })

        paper.on('element:pointermove', (elementView, evt, x, y) => {
          if (evt.data.draggedElement) {
            let {width, height} = evt.data.draggedElement.get('size')
            evt.data.draggedElement.set('position', {x: x - width/2, y: y - height/2})
          }
        })

        paper.on('link:pointerdown', (linkView, evt) => {
          if (evt.altKey) {
            linkView.model.remove()
          }
        })

        paper.on('blank:pointerdown', (evt, x, y) => {
          if (evt.shiftKey) {
            // create parent
            let width = 100
            let height = 50
            let parent = new joint.shapes.standard.Rectangle({
              position: { x: x - width/2, y: y - height/2 },
              size: { width, height },
            })
            this.styleNode(parent, 'new node', 'blank')
            parent.addTo(graph)
            // create child
            let child = new joint.shapes.standard.Rectangle({
              position: { x: x - width/2, y: y - height/2 },
              size: { width, height },
            })
            this.styleNode(child, 'new node', 'blank')
            child.addTo(graph)
            evt.data = evt.data ? evt.data : {}
            evt.data.draggedElement = child
            // create link
            let link = new joint.shapes.standard.Link()
            link.attr('line/strokeWidth', 1)
            link.source(parent)
            link.target(child)
            link.addTo(graph)
          }
        })

        paper.on('blank:pointermove', (evt, x, y) => {
          if (evt.data.draggedElement) {
            let {width, height} = evt.data.draggedElement.get('size')
            evt.data.draggedElement.set('position', {x: x - width/2, y: y - height/2})
          }
        })

        let tokens = this.tokenize(behaviorTreeString)
        this.drawNode(graph, null, this.parseTree(tokens, 0))
        let graphBBox = joint.layout.DirectedGraph.layout(graph, {
          dagre: dagre,
          graphlib: graphlib,
          nodeSep: 30,
          edgeSep: 80,
          marginX: 20,
          marginY: 2,
          rankDir: "LR",
        })

        paper.setDimensions(window.innerWidth, graphBBox.height + 4)
      },

      drawNode(graph, parent, nodeObj) {
        let node = new joint.shapes.standard.Rectangle()
        // calculate dimensions
        let width = 120
        let wrapText = joint.util.breakText(nodeObj.value || '', {width})
        let {height} = this.getTextSize(wrapText)
        node.resize(width + 25, height + 25)
        // style node and add label
        this.styleNode(node, wrapText, nodeObj.type)
        // draw self
        if (nodeObj.value !== null) {
          node.addTo(graph)
        }
        // draw link
        if (parent && parent.attr('label/text').length > 0) {
          let link = new joint.shapes.standard.Link()
          link.attr('line/strokeWidth', 1)
          link.source(parent)
          link.target(node)
          link.addTo(graph)
        }
        // draw children
        nodeObj.children.forEach(child => {
          this.drawNode(graph, node, child)
        })
      },

      getTextSize(text, font) {
        let lines = text.split('\n')
        let maxWidth = 0
        lines.forEach(line => {
          let currWidth = this.context.measureText(line).width
          if (currWidth > maxWidth) {
            maxWidth = currWidth
          }
        })
        let metrics = this.context.measureText(text);
        let height = 1.4 * lines.length * (metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent)
        return {width: maxWidth, height};
      },

      styleNode(node, text, type) {
        node.attr({
          body: {
            strokeWidth: 1,
          },
          label: {
            text: text,
            fill: 'black',
            fontFamily: this.font.family,
            fontSize: this.font.size,
          },
        })
        if (type === 'then') {
          node.attr('body/fill', 'lightcyan')
        } else if (type === 'condition') {
          node.attr('body/fill', 'lightyellow')
        } else if (type === 'action') {
          node.attr('body/fill', 'moccasin')
        } else if (type === 'definition') {
          node.attr('body/fill', 'pink')
        }
      },
    }
  }

  export default TreeDiagram;
</script>