// var alert_success = '<div class="alert alert-success"><button data-dismiss="alert" class="close" type="button"><i class="glyph-close"></i></button><div class="alert-icon"><i class="glyph-success"></i></div><div class="alert-body">Lorem ipsum dolor sit amet.</div></div>';
// var alert_warning = '<div class="alert alert-info"><div class="alert-icon"><i class="glyph-info"></i></div><div class="alert-body">Lorem ipsum dolor sit amet.</div></div>';
// var lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.";
// var excepteur_sint = "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

tinymce.init({
  language: "pl",
  language_url: "/static/congo_admin/js/tinymce/langs/pl.js",
  // selector: "textarea",
  mode: "specific_textareas",
  editor_selector: "vLargeTextField",
  editor_deselector: "plain_text",
  plugins: [
    "autolink lists link image charmap print preview anchor",
    "searchreplace visualblocks visualchars code fullscreen",
    "table contextmenu paste hr nonbreaking template"
  ],
  external_plugins: {
    // http://www.avoid.org/codemirror-for-tinymce4/
    // https://github.com/codemirror/CodeMirror
    "codemirror": "/static/congo_admin/js/tinymce/plugins/codemirror/plugin.min.js"
  },

  // toolbar: "styleselect common_tags | bold | alignleft aligncenter alignright alignjustify | bullist | link unlink image | preview code fullscreen",
  toolbar: "styleselect common_tags | bold | bullist numlist | link unlink image template | preview code fullscreen",
  
  width: 606,
  height: 200,
  resize: "both",
  // valid_elements: "*[*],b/strong,i/em",
  valid_elements: "*[*]",
  valid_children : "+body[style]",
  extended_valid_elements : "#i[class|style]",
  convert_urls: false,
  entity_encoding: "raw",
  paste_as_text: true,
  // content_css: "/static/custom_admin/js/tinymce/tinymce.css",
  
  menu: { 
      edit: {title: 'Edit', items: 'undo redo | cut copy paste pastetext | selectall searchreplace'}, 
      insert: {title: 'Insert', items: 'common_tags | link image template | charmap anchor hr nonbreaking'},
      view: {title: 'View', items: 'visualaid visualblocks visualchars | preview code fullscreen'}, 
      format: {title: 'Format', items: 'bold strikethrough superscript subscript | formats | removeformat'}, 
      table: {title: 'Table', items: 'inserttable tableprops deletetable cell row column'}, 
  },

  style_formats: [
    {title: "Paragraph", format: "p"},
    {title: "Div", format: "div"},
    {title: "Headers", items: [
      {title: "Header 1", format: "h1"},
      {title: "Header 2", format: "h2"},
      {title: "Header 3", format: "h3"},
      {title: "Header 4", format: "h4"},
      {title: "Header 5", format: "h5"},
      {title: "Header 6", format: "h6"}
    ]},
    {title: "Blocks", items: [
      {title: "Blockquote", format: "blockquote"},
      {title: "Pre", format: "pre"},
    ]},
    {title: "Inline", items: [
        {title: "Bold", icon: "bold", format: "bold"},
        {title: "Italic", icon: "italic", format: "italic"},
        // {title: "Underline", icon: "underline", format: "underline"},
        {title: "Strikethrough", icon: "strikethrough", format: "strikethrough"},
        {title: "Superscript", icon: "superscript", format: "superscript"},
        {title: "Subscript", icon: "subscript", format: "subscript"},
        {title: "Code", icon: "code", format: "code"}
    ]},
    {title: "Style", items: [
      {title: 'text-success', inline: 'span', classes: 'text-success'},
      {title: 'text-info', inline: 'span', classes: 'text-info'},
      {title: 'text-warning', inline: 'span', classes: 'text-warning'},
      {title: 'text-danger', inline: 'span', classes: 'text-danger'},
      {title: 'text-muted', inline: 'span', classes: 'text-muted'},
      // {title: "Code", format: "code"}
      // {title: 'row', selector: 'div', classes: 'row'},
      // {title: 'col-md-1', selector: 'div', classes: 'col-md-1'},
      // {title: 'col-md-offset-1', selector: 'div', classes: 'col-md-offset-1'},
      // {title: 'clearfix', selector: 'div', classes: 'clearfix'},
      // {title: 'pull-left', selector: 'div', classes: 'pull-left'},
      // {title: 'pull-right', selector: 'div', classes: 'pull-right'},
      // {title: 'show', selector: '*', classes: 'show'},
      // {title: 'hidden', classes: 'hidden'},
      // {title: 'visible-xs', classes: 'visible-xs'},
      // {title: 'hidden-xs', classes: 'hidden-xs'},
    ]},
    // {title: "Mailing", items: [
      // {title: 'green', inline: 'span', styles: {color: '#69A307'}},
      // {title: 'blue', inline: 'span', styles: {color: '#007ab9'}},
      // {title: 'red', inline: 'span', styles: {color: '#b90000'}},
      // {title: 'orange', inline: 'span', styles: {color: '#FF7920'}},
      // {title: 'yellow', inline: 'span', styles: {color: '#FFD000'}},
      // {title: 'gray', inline: 'span', styles: {color: '#666666'}},
    // ]},
    {title: "Alignment", items: [
        {title: "Left", icon: "alignleft", format: "alignleft"},
        {title: "Center", icon: "aligncenter", format: "aligncenter"},
        {title: "Right", icon: "alignright", format: "alignright"},
        {title: "Justify", icon: "alignjustify", format: "alignjustify"}
    ]}
  ],
  
  // templates: [
    // {
      // title: "Agata Gęsina (PL)",
      // url: "/static/custom_admin/js/tinymce/templates/agatagesina_pl.html",
      // description: "Do newslettera w jęz. PL"
    // },
    // {
      // title: "Agata Gęsina (EN)",
      // url: "/static/custom_admin/js/tinymce/templates/agatagesina_en.html",
      // description: "Do newslettera w jęz. EN"
    // },
    // {
      // title: "F. H. Faktor (PL)",
      // url: "/static/custom_admin/js/tinymce/templates/faktor_pl.html",
      // description: "Do newslettera w jęz. PL"
    // },
    // {
      // title: "F. H. Faktor (EN)",
      // url: "/static/custom_admin/js/tinymce/templates/faktor_en.html",
      // description: "Do newslettera w jęz. EN"
    // }
  // ],
  
  setup: function(editor) {
    editor.addButton('common_tags', {
      type: 'menubutton',
      text: '{...}',
      icon: false,
      menu: [
        {text: '{! greeting !}', onclick: function() {editor.insertContent('{! greeting !}');}},
        {text: '{% photo... %}', menu: [
          {text: '{% content_photo %}', onclick: function() {editor.insertContent('{% content_photo 123 %}');}},
          {text: '{% product_photo %}', onclick: function() {editor.insertContent('{% product_photo 123 %}');}},
          {text: '{% unrelated_photo %}', onclick: function() {editor.insertContent('{% unrelated_photo 123 %}');}},
          {text: '{% list_gallery %}', onclick: function() {editor.insertContent('{% list_gallery "url" %}');}},
          {text: '{% delivery_gallery %}', onclick: function() {editor.insertContent('{% delivery_gallery "url" %}');}},
          {text: '{% upcoming_delivery_gallery %}', onclick: function() {editor.insertContent('{% upcoming_delivery_gallery "url" %}');}}
        ]},
        {text: '{% video... %}', menu: [
          {text: '{% content_video %}', onclick: function() {editor.insertContent('{% content_video 123 %}');}},
          {text: '{% product_video %}', onclick: function() {editor.insertContent('{% product_video 123 %}');}}
        ]},
        {text: '{% other... %}', menu: [
          {text: '{! discount_code !}', onclick: function() {editor.insertContent('{! discount_code 1 !}');}},
          {text: '{% domain %}', onclick: function() {editor.insertContent('{% domain 1 %}');}},
          {text: '{% verbatim %}', onclick: function() {editor.selection.setContent('{% verbatim %}' + editor.selection.getContent() + '{% endverbatim %}');}}
        ]},
        {text: '<div />', menu: [
          {text: 'alert-success close', onclick: function() {editor.insertContent(alert_success);}},
          {text: 'alert-info', onclick: function() {editor.insertContent(alert_warning);}}
        ]},
        {text: 'Lorem...', menu: [
          {text: 'Lorem ipsum...', onclick: function() {editor.insertContent(lorem_ipsum);}},
          {text: 'Excepteur sint...', onclick: function() {editor.insertContent(excepteur_sint);}}
        ]}
      ]
    });
  },

  codemirror: {
    indentOnInit: true, // Whether or not to indent code on init. 
    path: '/static/codemirror/' // Path to CodeMirror distribution
  }
});
