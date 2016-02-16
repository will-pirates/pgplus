$(document).ready(function() {
  load({'experts': [['Belkin', '112043759976089842597']], 'engineers': [['Joe', '110257721827374623737'], ['Jason', '105193078925726528104']]});
});

function load(people){
  $("svg").remove();
  var width = 800,
      height = 400;

  var engineerNodes = [];
  if(people.engineers){
    engineerNodes = people.engineers.map(function(d){return {radius: 45, name: d[0], id: d[1], type: 'engineer'}});
  }
  var expertNodes = [];
  if(people.experts){
    expertNodes = people.experts.map(function(d){return {radius: 45, name: d[0], id: d[1], type: 'expert'}});
  }
  var rootNodes = [""].map(function(){return {radius: 5}});
  var nodes = rootNodes.concat(engineerNodes).concat(expertNodes),
      root = nodes[0],
      color = d3.scale.category10();

  var force = d3.layout.force()
      .gravity(0.05)
      .charge(function(d, i) { return i ? 0 : -2000; })
      .nodes(nodes)
      .size([width, height]);

  root.radius = 0;
  root.fixed = true;

  force.start();

  var svg = d3.select("#circles-container").append("svg")
      .attr("width", width)
      .attr("height", height);

  var svgNode = svg.selectAll(".node")
     .data(nodes.slice(1))
     .enter().append("g");

  svgNode.append("circle")
      .attr("r", function(d) { return d.radius; })
      .style("fill", function(d, i) {
        if(d.type == 'engineer'){
          return d3.rgb(255, 127, 14); 
        } 
        else {
          return d3.rgb(31, 119, 180);
        }
      });

  var label = svgNode.append("svg:text")
      .text(function (d) { return d.name; })
      .style("text-anchor", "middle")
      .style("font-family", "Arial")
      .style("font-size", 12);

  force.on("tick", function(e) {
    var q = d3.geom.quadtree(nodes),
        i = 0,
        n = nodes.length;

    while (++i < n) q.visit(collide(nodes[i]));

    svg.selectAll("circle")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    label.attr("x", function(d){return d.x;})
         .attr("y", function(d){return d.y;})
  });

  svg.on("mousemove", function() {
    var p1 = d3.mouse(this);
    root.px = p1[0];
    root.py = p1[1];
    force.resume();
  });
}

function collide(node) {
  var r = node.radius + 16,
      nx1 = node.x - r,
      nx2 = node.x + r,
      ny1 = node.y - r,
      ny2 = node.y + r;
  return function(quad, x1, y1, x2, y2) {
    if (quad.point && (quad.point !== node)) {
      var x = node.x - quad.point.x,
          y = node.y - quad.point.y,
          l = Math.sqrt(x * x + y * y),
          r = node.radius + quad.point.radius;
      if (l < r) {
        l = (l - r) / l * .5;
        node.x -= x *= l;
        node.y -= y *= l;
        quad.point.x += x;
        quad.point.y += y;
      }
    }
    return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
  };
}
