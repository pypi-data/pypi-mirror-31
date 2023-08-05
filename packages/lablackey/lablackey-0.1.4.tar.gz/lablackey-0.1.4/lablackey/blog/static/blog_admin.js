if (document.querySelector("#blogForm #id_content")) {
  var insert_photo = {
    name: "insert-photo",
    action: function customFunction(editor){
      var cm = editor.codemirror;
      insertImage(cm.getSelection(),function(result) {
        cm.replaceSelection(result.shortcode);
      })
    },
    className: "fa fa-image",
    title: "Custom Button",
  };
  new SimpleMDE({
    element: document.querySelector("textarea"),
    spellChecker: false,
    toolbar: [
      'bold','italic','heading','|',
      'quote','unordered-list','ordered-list','|',
      'link', insert_photo, "|",
      'preview','side-by-side','fullscreen',"|",
    ],
  });
};

