<template>
  <div id="behaviorTreeDiagram"></div>
</template>

<script>
  import * as joint from 'jointjs'

  // todo: get string from GET request to API
  // move analyzing node type into tokenizer
  // separate different graphs
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

  const BehaviorTreeDiagram = {
    components: {},
    props: [],
    data() {
      return {
      }
    },
    mounted() {
      this.drawBehaviorTree(this.parseTree(this.tokenize(behaviorTreeString), 0))
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
          let value = line.slice(tabs)
          tokens.push({tabs, value})
        })
        return tokens
      },

      analyzeLevels(tokens) {
        let levels = []
        tokens.forEach(token => {
          if (token.tabs < 0) {
            return
          }
          if (levels[token.tabs] === undefined) {
            levels[token.tabs] = 1
          } else {
            levels[token.tabs]++
          }
        })
        return levels
      },

      parseTree(tokens, index) {
        // base case: leaf node; no next elt or next elt's tabs <= curr elt's tabs
        if (tokens.length <= index + 1 || tokens[index + 1].tabs <= tokens[index].tabs) {
          return {
            value: tokens[index].value,
            children: [],
          }
        } else {
          // loop through children
          let childIndex = index + 1
          let children = []
          while (childIndex < tokens.length && tokens[childIndex].tabs > tokens[index].tabs) {
            if (tokens[childIndex].tabs === tokens[index].tabs + 1) {
              children.push(this.parseTree(tokens, childIndex))
            }
            childIndex++
          }
          return {
            value: tokens[index].value,
            children,
          }
        }
      },

      drawBehaviorTree(treeObj) {
        let graph = new joint.dia.Graph
        let paperSize = {width: window.innerWidth, height: window.innerHeight}

        let paper = new joint.dia.Paper({
          el: document.getElementById('behaviorTreeDiagram'),
          model: graph,
          width: paperSize.width,
          height: paperSize.height,
          gridSize: 1,
        })

        let tokens = this.tokenize(behaviorTreeString)
        let levels = this.analyzeLevels(tokens)
        let margin = 40
        let node = new joint.shapes.standard.Rectangle()
        node.resize(0, paperSize.height/levels.length - margin*2)
        node.attr({

        })

        this.drawNode(paperSize, margin, levels, new Array(levels.length).fill(0), graph, null, this.parseTree(tokens, 0), -1)
      },

      drawNode(paperSize, margin, levelCaps, levelFilled, graph, parent, nodeObj, level) {
        console.log(parent)
        let node = new joint.shapes.standard.Rectangle()
        let width = paperSize.width/levelCaps[level] - margin*2
        let height = paperSize.height/levelCaps.length - margin*2
        node.resize(width, height)
        let wrapText = joint.util.breakText(nodeObj.value || '', {width})
        node.attr({
          label: {
            text: wrapText,
            fill: 'black',
          }
        })
        this.styleNode(node)
        node.position((width + margin*2) * levelFilled[level] + margin, 
          (height + margin*2) * level + margin)
        // draw self
        if (level >= 0) {
          node.addTo(graph)
        }
        // draw link
        if (level > 0) {
          let link = new joint.shapes.standard.Link();
          console.log(parent.attr('label/text'))
          link.source(parent)
          link.target(node)
          link.addTo(graph)
        }
        // draw children
        levelFilled[level]++
        console.log(node)
        nodeObj.children.forEach(child => {
          this.drawNode(paperSize, margin, levelCaps, levelFilled, graph, node, child, level + 1)
        })
      },

      styleNode(node) {
        let value = node.attr('label/text')
        if (value.startsWith('then')) {
          node.attr('body/fill', 'lightcyan')
        } else if (value.startsWith('unless')) {
          node.attr('body/fill', 'lightyellow')
        } else if (value.startsWith('wait') || value.startsWith('continue')) {
          node.attr('body/fill', 'moccasin')
        } else {
          node.attr('body/fill', 'pink')
        }
      },
    }
  }

  export default BehaviorTreeDiagram;
</script>