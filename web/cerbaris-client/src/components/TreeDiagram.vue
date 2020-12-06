<template>
  <div id="behaviorTreeDiagram"></div>
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
do something
\tthen
\t\tdo another thing
do blah
\tthen
\t\tdo blah2
`

  const TreeDiagram = {
    props: ['currNodeId'],
    watch: {
      currNodeId() {
        if (this.currPath) {
          this.changeStroke(this.currPath.nodes, this.currPath.links, 1, 'black')
        }
        if (this.currNodeId !== null) {
          this.currPath = this.getPathToRoot(this.nodeList[this.currNodeId], 
            {nodes: [], links: []})
          this.changeStroke(this.currPath.nodes, this.currPath.links, 2, 'red')
        }
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
      if (this.currNodeId !== null) {
        this.currPath = this.getPathToRoot(this.nodeList[this.currNodeId], {nodes: [], links: []})
        this.changeStroke(this.currPath.nodes, this.currPath.links, 2, 'red')
      }
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
          let type = this.determineType(tabs === 0, value)
          tokens.push({tabs, value, type})
        })
        return tokens
      },

      determineType(root, value) {
        if (value.startsWith('then')) {
          return 'then'
        } else if (value.startsWith('unless')) {
          return 'condition'
        } else if (root) {
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
        this.graph = new joint.dia.Graph
        let paperSize = {width: window.innerWidth, height: window.innerHeight * 0.85}

        let paper = new joint.dia.Paper({
          el: document.getElementById('behaviorTreeDiagram'),
          model: this.graph,
          width: paperSize.width,
          height: paperSize.height,
          gridSize: 1,
          interactive: true,
        })

//         paper.on('element:pointerdown', (elementView, evt, x, y) => {
//           if (evt.shiftKey) {
//             // prevent element from being dragged
//             elementView.options.interactive = false
//             let width = 145
//             let height = 50
//             let child = new joint.shapes.standard.Rectangle({
//               position: { x: x - width/2, y: y - height/2 },
//               size: { width, height },
//             })
//             this.styleNode(child, 'new node', 'blank')
//             child.addTo(this.graph)
//             evt.data.draggedElement = child
//             // create link
//             let link = new joint.shapes.standard.Link()
//             link.attr('line/strokeWidth', 1)
//             link.source(elementView.model)
//             link.target(child)
//             link.addTo(this.graph)
//           } else {
//             elementView.options.interactive = true
//           }
// 
//           if (evt.altKey) {
//             elementView.model.remove()
//           }
//         })
// 
//         paper.on('element:pointermove', (elementView, evt, x, y) => {
//           if (evt.data.draggedElement) {
//             let {width, height} = evt.data.draggedElement.get('size')
//             evt.data.draggedElement.set('position', {x: x - width/2, y: y - height/2})
//           }
//         })
// 
//         paper.on('element:pointerdblclick', (elementView, evt) => {
//           let text = prompt('Enter new text:')
//           if (text) {
//             elementView.model.attr('label/text', text)
//             let links = this.graph.getConnectedLinks(elementView.model, { inbound: true })
//             this.styleNode(elementView.model, text, this.determineType(links.length === 0, text))
//           }
//         })
// 
//         paper.on('link:pointerdown', (linkView, evt) => {
//           if (evt.altKey) {
//             linkView.model.remove()
//           }
//         })
// 
//         paper.on('blank:pointerdown', (evt, x, y) => {
//           if (evt.shiftKey) {
//             // create parent
//             let width = 145
//             let height = 50
//             let parent = new joint.shapes.standard.Rectangle({
//               position: { x: x - width/2, y: y - height/2 },
//               size: { width, height },
//             })
//             this.styleNode(parent, 'new node', 'blank')
//             parent.addTo(this.graph)
//             // create child
//             let child = new joint.shapes.standard.Rectangle({
//               position: { x: x - width/2, y: y - height/2 },
//               size: { width, height },
//             })
//             this.styleNode(child, 'new node', 'blank')
//             child.addTo(this.graph)
//             evt.data = evt.data ? evt.data : {}
//             evt.data.draggedElement = child
//             // create link
//             let link = new joint.shapes.standard.Link()
//             link.attr('line/strokeWidth', 1)
//             link.source(parent)
//             link.target(child)
//             link.addTo(this.graph)
//           }
//         })
// 
//         paper.on('blank:pointermove', (evt, x, y) => {
//           if (evt.data.draggedElement) {
//             let {width, height} = evt.data.draggedElement.get('size')
//             evt.data.draggedElement.set('position', {x: x - width/2, y: y - height/2})
//           }
//         })

        let tokens = this.tokenize(behaviorTreeString)
        this.nodeList = []
        this.drawNode(this.graph, null, this.parseTree(tokens, 0))
        let marginX = 20
        let marginY = 2
        let graphBBox = joint.layout.DirectedGraph.layout(this.graph, {
          dagre: dagre,
          graphlib: graphlib,
          nodeSep: 30,
          edgeSep: 80,
          marginX: marginX,
          marginY: marginY,
          rankDir: "LR",
        })

        let scale = Math.min(paperSize.width / (graphBBox.width + marginX*2), 
          paperSize.height / (graphBBox.height + marginY*2))
        paper.scale(scale, scale)
      },

      drawNode(graph, parent, nodeObj) {
        let node = new joint.shapes.standard.Rectangle()
        // style node and add label
        this.styleNode(node, nodeObj.value, nodeObj.type)
        // draw self
        if (nodeObj.value !== null) {
          node.addTo(graph)
          this.nodeList.push(node)
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
        // calculate dimensions
        let width = 120
        let wrapText = joint.util.breakText(text || '', {width})
        let {height} = this.getTextSize(wrapText)
        node.resize(width + 25, height + 25)
        node.attr({
          body: {
            strokeWidth: 1,
          },
          label: {
            text: wrapText,
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

      getPathToRoot(node, path) {
        // base case: node is root
        path.nodes.push(node)
        let links = this.graph.getConnectedLinks(node, { inbound: true })
        if (links.length > 0) {
          links.forEach(link => {
            path.links.push(link)
            this.getPathToRoot(link.getSourceElement(), path)
          })
        }
        return path
      },

      changeStroke(nodes, links, strokeWidth, stroke) {
        nodes.forEach(node => {
          node.attr({
            body: {
              strokeWidth,
              stroke,
            }
          })
        })

        links.forEach(link => {
          link.attr({
            line: {
              strokeWidth,
              stroke,
            }
          })
        })
      },

      serializeTree() {
        let roots = this.graph.getSources()
        roots.sort((firstElt, secondElt) => firstElt.get('position').y - secondElt.get('position').y)
        let text = ''
        roots.forEach(root => {
          text += this.serializeNode(root, 0)
        })
        return text
      },

      serializeNode(node, tabs) {
        // base case: leaf node
        let text = '\n'
        for (let i = 0; i < tabs; i++) {
          text += '\t'
        }
        text += node.attr('label/text').replace('\n', ' ')
        let links = this.graph.getConnectedLinks(node, { outbound: true })
        if (links.length > 0) {
          let children = []
          links.forEach(link => {
            children.push(link.getTargetElement())
          })
          children.sort((firstElt, secondElt) => firstElt.get('position').y - secondElt.get('position').y)
          children.forEach(child => {
            text += this.serializeNode(child, tabs + 1)
          })
        }
        return text
      },
    }
  }

  export default TreeDiagram;
</script>