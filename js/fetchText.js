function selectFieldText(field) {
  const range = document.createRange();
  range.selectNodeContents(field);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}
function fetchText() {
  const sel = window.getSelection();
  console.log("Selection object:", sel);

  let field;
  if (sel.rangeCount > 0) {
    field = get_field(sel);
  } else {
    field = document.querySelector(".rich-text-input"); // Adjust the selector to match your field
    if (field) {
      selectFieldText(field);
    }
  }

  console.log("Field:", field);
  if (field) {
    const text = getFieldText(field);
    console.log("Field content:", text);

    const currentField = window.currentField || window.parent.currentField;
    if (!currentField) {
      console.error("currentField is not defined");
      return;
    }
    pycmd("textToJReading:||:||:" + text + ':||:||:' + currentField.id.substring(1) + ':||:||:' + currentNoteId);
  } else {
    console.error("Field is null");
  }
}

try {
  fetchText();
} catch (e) {
  alert(e);
}