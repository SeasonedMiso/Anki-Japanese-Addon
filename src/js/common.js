
function unnest_span(span) {
  span.normalize();
  var result = [];
  for (var i = 0; i < span.childNodes.length; i++) {
    var node = span.childNodes[i];
    if (node.nodeName === "SPAN") {
      if (node.childNodes.length === 1) {
        result.push(node);
      } else if (node.childNodes.length > 1) {
        result.push.apply(result, unnest_span(node));
      }
    } else {
      var new_span = span.cloneNode(false);
      new_span.innerHTML = "";
      new_span.appendChild(node.cloneNode(true));
      result.push(new_span);
    }
  }
  return result;
}

function selectAllFieldNodes(field, sel){
  setFormat("inserthtml", '');
  const newRange = new Range();
  sel.removeAllRanges();
  newRange.selectNodeContents(field);
  sel.addRange(newRange)
}

function selectText(node, sel) {
    sel.selectAllChildren(node)

}


function clean_field(field) {
  var new_field = document.createDocumentFragment();
  for (var i = 0; i < field.childNodes.length; i++) {
    var node = field.childNodes[i];
    if (node.nodeName === "SPAN") {
      var new_nodes = unnest_span(node);
      for (var j = 0; j < new_nodes.length; j++) {
        new_field.appendChild(new_nodes[j]);
      }
    } else {
      new_field.appendChild(node.cloneNode(true));
    }
  }
  field.innerHTML = "";
  field.appendChild(new_field);
}

function is_field(node) {
  console.log("Checking node:", node);
  console.log("Node name:", node.nodeName);
  if (node.classList) {
    console.log("Node classes:", Array.from(node.classList));
  } else {
    console.log("Node has no class list");
  }
   return node.nodeName === "DIV" && node.classList.contains("rich-text-input");
}

function get_field(sel) {
  var node = sel.baseNode || sel.anchorNode || sel.focusNode;
  console.log("Starting node:", node);
  while (node && !is_field(node)) {
    node = node.parentNode;
    console.log("Parent Node:", node);
  }
  return node;
}

