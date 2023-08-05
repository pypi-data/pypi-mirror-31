from z3 import Z3Exception, simplify
from laser.ethereum.svm import NodeFlags
import re

default_title = '<p>Mythril / Ethereum LASER Symbolic VM</p>'

default_style = '''
  <style type="text/css">
   #mynetwork {
    background-color: #232625;
   }

   body {
    background-color: #232625;
    color: #ffffff;
    font-size: 10px;
   }
  </style>
'''

default_opts = '''
   var options = {
      autoResize: true,
      height: '100%',
      width: '100%',
      manipulation: false,
      height: '90%',
      layout: {
        randomSeed: undefined,
        improvedLayout:true,
        hierarchical: {
          enabled:true,
          levelSeparation: 450,
          nodeSpacing: 200,
          treeSpacing: 100,
          blockShifting: true,
          edgeMinimization: true,
          parentCentralization: false,
          direction: 'LR',        // UD, DU, LR, RL
          sortMethod: 'directed'   // hubsize, directed
        }
      },
      nodes:{
        borderWidth: 1,
        borderWidthSelected: 2,
        chosen: true,
        shape: 'box',
        font: {
          align: 'left',
          color: '#FFFFFF',
        },
      },
      edges:{
        font: {
          color: '#ffffff',
          size: 12, // px
          face: 'arial',
          background: 'none',
          strokeWidth: 0, // px
          strokeColor: '#ffffff',
          align: 'horizontal',
          multi: false,
          vadjust: 0,
        }
      },

      physics:{
        enabled: [ENABLE_PHYSICS],
      }

  }
'''


phrack_style = '''
  <style type="text/css">
   #mynetwork {
    background-color: #ffffff;
   }

   body {
    background-color: #ffffff;
    color: #000000;
    font-size: 10px;
    font-family: "courier new";
   }


  </style>
'''

phrack_opts = '''
    var options = {
      autoResize: true,
      height: '100%',
      width: '100%',
      manipulation: false,
      height: '90%',
      layout: {
        randomSeed: undefined,
        improvedLayout:true,
        hierarchical: {
          enabled:true,
          levelSeparation: 450,
          nodeSpacing: 200,
          treeSpacing: 100,
          blockShifting: true,
          edgeMinimization: true,
          parentCentralization: false,
          direction: 'LR',        // UD, DU, LR, RL
          sortMethod: 'directed'   // hubsize, directed
        }
      },
      nodes:{
        color: '#000000',
        borderWidth: 1,
        borderWidthSelected: 1,
        shapeProperties: {
          borderDashes: false, // only for borders
          borderRadius: 0,     // only for box shape
        },
        chosen: true,
        shape: 'box',
        font: {
          face: 'courier new',
          align: 'left',
          color: '#000000',
        },
      },
      edges:{
        font: {
          color: '#000000',
          face: 'courier new',
          background: 'none',
          strokeWidth: 0, // px
          strokeColor: '#ffffff',
          align: 'horizontal',
          multi: false,
          vadjust: 0,
        }
      },

      physics:{
        enabled: [ENABLE_PHYSICS],
      }
  }
'''

graph_html = '''<html>
 <head>

  [STYLE]

  <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
  <script>

  [OPTS]

  [JS]

  </script>
 </head>
<body>
<p>Mythril / LASER Symbolic VM</p>
<p><div id="mynetwork"></div><br/></p>
<script type="text/javascript">
var container = document.getElementById('mynetwork');

var nodesSet = new vis.DataSet(nodes);
var edgesSet = new vis.DataSet(edges);
var data = {'nodes': nodesSet, 'edges': edgesSet}

var gph = new vis.Network(container, data, options);
gph.on("click", function (params) {
  // parse node id
  var nodeID = params['nodes']['0'];
  if (nodeID) {
    var clickedNode = nodesSet.get(nodeID);

    if(clickedNode.isExpanded) {
      clickedNode.label = clickedNode.truncLabel;
    }
    else {
      clickedNode.label = clickedNode.fullLabel;
    }

    clickedNode.isExpanded = !clickedNode.isExpanded;

    nodesSet.update(clickedNode);
  }
});
</script>
</body>
</html>
'''

colors = [
    "{border: '#26996f', background: '#2f7e5b', highlight: {border: '#26996f', background: '#28a16f'}}",
    "{border: '#9e42b3', background: '#842899', highlight: {border: '#9e42b3', background: '#933da6'}}",
    "{border: '#b82323', background: '#991d1d', highlight: {border: '#b82323', background: '#a61f1f'}}",
    "{border: '#4753bf', background: '#3b46a1', highlight: {border: '#4753bf', background: '#424db3'}}",
    "{border: '#26996f', background: '#2f7e5b', highlight: {border: '#26996f', background: '#28a16f'}}",
    "{border: '#9e42b3', background: '#842899', highlight: {border: '#9e42b3', background: '#933da6'}}",
    "{border: '#b82323', background: '#991d1d', highlight: {border: '#b82323', background: '#a61f1f'}}",
    "{border: '#4753bf', background: '#3b46a1', highlight: {border: '#4753bf', background: '#424db3'}}",
]


def serialize(statespace, color_map):

    nodes = []
    edges = []

    for node_key in statespace.nodes:

        node = statespace.nodes[node_key]

        code = node.get_cfg_dict()['code']
        code = re.sub("([0-9a-f]{8})[0-9a-f]+", lambda m: m.group(1) + "(...)", code)

        if NodeFlags.FUNC_ENTRY in node.flags:
            code = re.sub("JUMPDEST", node.function_name, code)

        code_split = code.split("\\n")

        truncated_code = code if (len(code_split) < 7) else "\\n".join(code_split[:6]) + "\\n(click to expand +)"

        color = color_map[node.get_cfg_dict()['contract_name']]

        nodes.append("{id: '" + str(node_key) + "', color: " + color + ", size: 150, 'label': '" + truncated_code + "', 'fullLabel': '" + code + "', 'truncLabel': '" + truncated_code + "', 'isExpanded': false}")

    for edge in statespace.edges:

        if (edge.condition is None):
            label = ""
        else:

            try:
                label = str(simplify(edge.condition)).replace("\n", "")
            except Z3Exception:
                label = str(edge.condition).replace("\n", "")

        label = re.sub("([^_])([\d]{2}\d+)", lambda m: m.group(1) + hex(int(m.group(2))), label)
        code = re.sub("([0-9a-f]{8})[0-9a-f]+", lambda m: m.group(1) + "(...)", code)

        edges.append("{from: '" + str(edge.as_dict()['from']) + "', to: '" + str(edge.as_dict()['to']) + "', 'arrows': 'to', 'label': '" + label + "', 'smooth': {'type': 'cubicBezier'}}")

    return "var nodes = [\n" + ",\n".join(nodes) + "\n];\nvar edges = [\n" + ",\n".join(edges) + "\n];"


def generate_graph(statespace, physics=False, phrackify=False):
    '''
    This is some of the the ugliest code in the whole project.
    At some point someone needs to write a templating system.
    '''

    color_map = {}

    if phrackify:

        for k in statespace.accounts:
            color_map[statespace.accounts[k].contract_name] = "{border: '#000000', background: '#ffffff', highlight: {border: '#000000', background: '#ffffff'}}"

        html = graph_html.replace("[STYLE]", phrack_style).replace("[OPTS]", phrack_opts)

    else:

        i = 0

        for k in statespace.accounts:
            color_map[statespace.accounts[k].contract_name] = colors[i]
            i += 1

        html = graph_html.replace("[STYLE]", default_style).replace("[OPTS]", default_opts)

    html = html.replace("[JS]", serialize(statespace, color_map)).replace("[ENABLE_PHYSICS]", str(physics).lower())

    return html
