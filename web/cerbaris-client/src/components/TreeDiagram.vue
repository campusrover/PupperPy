<template>
  <div id="behaviorTreeDiagram" />
</template>

<script>
import * as joint from 'jointjs'
import dagre from 'dagre'
import graphlib from 'graphlib'

const behaviorTreeString = `root
\tAvoid Obstacles
\tMove Until Target Found
\tGo To Target
`

const TreeDiagram = {
  props: ['currNodeId'],
  watch: {
    currNodeId () {
      if (this.currPath) {
        this.changeStroke(this.currPath.nodes, this.currPath.links, 1, 'black')
      }
      if (this.currNodeId !== null) {
        this.currPath = this.getPathToRoot(this.nodeList[this.currNodeId], {
          nodes: [],
          links: [],
        })
        this.changeStroke(this.currPath.nodes, this.currPath.links, 2, 'red')
      }
    },
  },
  mounted () {
    this.context = document.createElement('canvas').getContext('2d')
    this.font = {
      size: 14,
      family: 'Helvetica',
    }
    this.context.font = this.font.size + 'px ' + this.font.family
    this.drawTree(this.parseTree(this.tokenize(behaviorTreeString), 0))
    if (this.currNodeId !== null) {
      this.currPath = this.getPathToRoot(this.nodeList[this.currNodeId], {
        nodes: [],
        links: [],
      })
      this.changeStroke(this.currPath.nodes, this.currPath.links, 2, 'red')
    }
  },
  methods: {
    tokenize (text) {
      const lines = text.split('\n')
      const tokens = []
      tokens.push({ tabs: -1, value: null }) // root

      lines.forEach((line) => {
        if (line.trim().length === 0) {
          return
        }
        const tabs = line.lastIndexOf('\t') + 1
        const value = line.trim()
        const type = this.determineType(tabs === 0, value)
        tokens.push({ tabs, value, type })
      })
      return tokens
    },

    determineType (root, value) {
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

    parseTree (tokens, index) {
      const node = {
        value: tokens[index].value,
        type: tokens[index].type,
      }
      // base case: leaf node; no next elt or next elt's tabs <= curr elt's tabs
      if (
        tokens.length <= index + 1 ||
        tokens[index + 1].tabs <= tokens[index].tabs
      ) {
        node.children = []
        return node
      } else {
        // loop through children and call recursively
        let childIndex = index + 1
        const children = []
        while (
          childIndex < tokens.length &&
          tokens[childIndex].tabs > tokens[index].tabs
        ) {
          if (tokens[childIndex].tabs === tokens[index].tabs + 1) {
            children.push(this.parseTree(tokens, childIndex))
          }
          childIndex++
        }
        node.children = children
        return node
      }
    },

    drawTree (treeObj) {
      this.graph = new joint.dia.Graph()
      const paperSize = {
        width: window.innerWidth,
        height: window.innerHeight * 0.85,
      }

      const paper = new joint.dia.Paper({
        el: document.getElementById('behaviorTreeDiagram'),
        model: this.graph,
        width: paperSize.width,
        height: paperSize.height,
        gridSize: 1,
        interactive: true,
      })

      paper.on('element:pointerdown', (elementView, evt, x, y) => {
        if (evt.shiftKey) {
          // prevent element from being dragged
          elementView.options.interactive = false
          const width = 145
          const height = 50
          const child = new joint.shapes.standard.Rectangle({
            position: { x: x - width / 2, y: y - height / 2 },
            size: { width, height },
          })
          this.styleNode(child, 'new node', 'blank')
          child.addTo(this.graph)
          evt.data.draggedElement = child
          // create link
          const link = new joint.shapes.standard.Link()
          link.attr('line/strokeWidth', 1)
          link.source(elementView.model)
          link.target(child)
          link.addTo(this.graph)
        } else {
          elementView.options.interactive = true
        }

        if (evt.altKey) {
          elementView.model.remove()
        }
      })

      paper.on('element:pointermove', (elementView, evt, x, y) => {
        if (evt.data.draggedElement) {
          const { width, height } = evt.data.draggedElement.get('size')
          evt.data.draggedElement.set('position', {
            x: x - width / 2,
            y: y - height / 2,
          })
        }
      })

      paper.on('element:pointerdblclick', (elementView, evt) => {
        const text = prompt('Enter new text:')
        if (text) {
          elementView.model.attr('label/text', text)
          const links = this.graph.getConnectedLinks(elementView.model, {
            inbound: true,
          })
          this.styleNode(
            elementView.model,
            text,
            this.determineType(links.length === 0, text),
          )
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
          const width = 145
          const height = 50
          const parent = new joint.shapes.standard.Rectangle({
            position: { x: x - width / 2, y: y - height / 2 },
            size: { width, height },
          })
          this.styleNode(parent, 'new node', 'blank')
          parent.addTo(this.graph)
          // create child
          const child = new joint.shapes.standard.Rectangle({
            position: { x: x - width / 2, y: y - height / 2 },
            size: { width, height },
          })
          this.styleNode(child, 'new node', 'blank')
          child.addTo(this.graph)
          evt.data = evt.data ? evt.data : {}
          evt.data.draggedElement = child
          // create link
          const link = new joint.shapes.standard.Link()
          link.attr('line/strokeWidth', 1)
          link.source(parent)
          link.target(child)
          link.addTo(this.graph)
        }
      })

      paper.on('blank:pointermove', (evt, x, y) => {
        if (evt.data.draggedElement) {
          const { width, height } = evt.data.draggedElement.get('size')
          evt.data.draggedElement.set('position', {
            x: x - width / 2,
            y: y - height / 2,
          })
        }
      })

      const tokens = this.tokenize(behaviorTreeString)
      this.nodeList = []
      this.drawNode(this.graph, null, this.parseTree(tokens, 0))
      const marginX = 20
      const marginY = 2
      const graphBBox = joint.layout.DirectedGraph.layout(this.graph, {
        dagre: dagre,
        graphlib: graphlib,
        nodeSep: 30,
        edgeSep: 80,
        marginX: marginX,
        marginY: marginY,
        rankDir: 'LR',
      })

      const scale = Math.min(1,
        paperSize.width / (graphBBox.width + marginX * 2),
        paperSize.height / (graphBBox.height + marginY * 2),
      )
      paper.scale(scale, scale)
    },

    drawNode (graph, parent, nodeObj) {
      const node = new joint.shapes.standard.Rectangle()
      // style node and add label
      this.styleNode(node, nodeObj.value, nodeObj.type)
      // draw self
      if (nodeObj.value !== null) {
        node.addTo(graph)
        this.nodeList.push(node)
      }
      // draw link
      if (parent && parent.attr('label/text').length > 0) {
        const link = new joint.shapes.standard.Link()
        link.attr('line/strokeWidth', 1)
        link.source(parent)
        link.target(node)
        link.addTo(graph)
      }
      // draw children
      nodeObj.children.forEach((child) => {
        this.drawNode(graph, node, child)
      })
    },

    getTextSize (text, font) {
      const lines = text.split('\n')
      let maxWidth = 0
      lines.forEach((line) => {
        const currWidth = this.context.measureText(line).width
        if (currWidth > maxWidth) {
          maxWidth = currWidth
        }
      })
      const metrics = this.context.measureText(text)
      const height =
        1.4 *
        lines.length *
        (metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent)
      return { width: maxWidth, height }
    },

    styleNode (node, text, type) {
      // calculate dimensions
      const width = 120
      const wrapText = joint.util.breakText(text || '', { width })
      const { height } = this.getTextSize(wrapText)
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

    getPathToRoot (node, path) {
      // base case: node is root
      path.nodes.push(node)
      const links = this.graph.getConnectedLinks(node, { inbound: true })
      if (links.length > 0) {
        links.forEach((link) => {
          path.links.push(link)
          this.getPathToRoot(link.getSourceElement(), path)
        })
      }
      return path
    },

    changeStroke (nodes, links, strokeWidth, stroke) {
      nodes.forEach((node) => {
        node.attr({
          body: {
            strokeWidth,
            stroke,
          },
        })
      })

      links.forEach((link) => {
        link.attr({
          line: {
            strokeWidth,
            stroke,
          },
        })
      })
    },

    serializeTree () {
      const roots = this.graph.getSources()
      roots.sort(
        (firstElt, secondElt) =>
          firstElt.get('position').y - secondElt.get('position').y,
      )
      let text = ''
      roots.forEach((root) => {
        text += this.serializeNode(root, 0)
      })
      return text
    },

    serializeNode (node, tabs) {
      // base case: leaf node
      let text = '\n'
      for (let i = 0; i < tabs; i++) {
        text += '\t'
      }
      text += node.attr('label/text').replace('\n', ' ')
      const links = this.graph.getConnectedLinks(node, { outbound: true })
      if (links.length > 0) {
        const children = []
        links.forEach((link) => {
          children.push(link.getTargetElement())
        })
        children.sort(
          (firstElt, secondElt) =>
            firstElt.get('position').y - secondElt.get('position').y,
        )
        children.forEach((child) => {
          text += this.serializeNode(child, tabs + 1)
        })
      }
      return text
    },
  },
}

export default TreeDiagram
</script>
