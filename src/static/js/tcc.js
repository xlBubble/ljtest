var Tcc = window.Tcc = {};

if (typeof window.jQuery == "undefined") {
  document.write('<script type="text/javascript" src="' + Tcc.base + 'js/jquery-1.3.2.min.js' + '" />');
}

jQuery.extend({
  getScriptEx : function (jsurl, fCallback) {
    var head = document.getElementsByTagName("head")[0];
    var script = document.createElement("script");
    script.src = jsurl;
    script.charset = "utf-8";

    // Handle Script loading
    var done = false;

    // Attach handlers for all browsers
    script.onload = script.onreadystatechange = function(){
      if ( !done && (!this.readyState ||
          this.readyState == "loaded" || this.readyState == "complete") ) {
        done = true;
        fCallback();
        head.removeChild( script );
      }
    };

    head.appendChild(script);
  }
});

Tcc.UserChooser = function(args) {
  args.choosertype = args.choosertype || 1;
  args.inputType = args.inputType || 1;
  this.initUserChooser(args);
};

Tcc.RichEditor = function(args) {
    document.write('<input id="' + args.id + '" name="' + args.name + '" type="hidden" richeditor="true" value="" />');
    document.write('<link href="' + Tcc.base +'js/tcc/qqmaileditor/editor.css" type="text/css" rel="stylesheet" />');
    if(!args.height)
        args.height = "260px";
    document.write('<div><iframe id="HtmlEditor" class="editor_frame" style="height:'+args.height+';" frameBorder="0" marginHeight=0 marginWidth=0 src="' + Tcc.base + 'js/tcc/qqmaileditor/blank.html' + '?domain=' + document.domain + '"></iframe></div>');
    $(document).ready(function() {
        var _loadEditor = function() {$.getScriptEx(Tcc.base +'js/tcc/qqmaileditor.js?r=3', function(){initRichEditor(args);});};
        if (typeof window.jQuery.fn.offset == "undefined") {
          $.getScriptEx(Tcc.base +'js/jquery.dimensions.js', _loadEditor);
        } else {
          _loadEditor();
        }
    });
};

Tcc.QmEditor = function(args) {
    var value = args.value || '';
    args.editorId = args.editorId || args.id + 'Editor';
    args.editorAreaId = args.editorAreaId || args.id + 'EditorArea';
    args.height = args.height || '260px';
    args.editorAreaWin = window;

    document.write('<input id="' + args.id + '" name="' + args.name + '" type="hidden" richeditor="true" value="" />');
    document.write('<div id="' + args.editorAreaId + '"></div>');
    document.write('<link href="' + Tcc.base +'js/tcc/qmeditor/style/comm.css?r=2" type="text/css" rel="stylesheet" />');

    $.getScriptEx(Tcc.base + 'js/tcc/qmeditor/editor.js?r=18', function(){
        var qe = new qmEditor(args);
        if (args.initDelay) {
        	setTimeout(function(){qe.initialize(value, true, 1)}, 1);
        } else {
        	qe.initialize(value, true, 1);
        }
        $('form').submit(function() {
            $('#' + args.id).val(qe.getContent());
        });
    });
};

/*
* lazy load rich editor
* author : franky
**/
Tcc.LazyQMEditor = function(args, loader_element) {
	args.needFocus = 1;
    var value = args.value || '';
    args.editorId = args.editorId || args.id + 'Editor';
    args.editorAreaId = args.editorAreaId || args.id + 'EditorArea';
    args.height = args.height || '260px';
    args.editorAreaWin = window;
	loader_element.parentNode.removeChild(loader_element);
    var LazyQMEditorContainer = document.getElementById('LazyQMEditorContainer');
    var fNewNode = document.createElement("INPUT");
    fNewNode.setAttribute('type', 'hidden');
    fNewNode.setAttribute('id',  args.id);
    fNewNode.setAttribute('name', args.name);
    fNewNode.setAttribute('richeditor', true);
    fNewNode.setAttribute('value', '');
    LazyQMEditorContainer.appendChild(fNewNode);
	fNewNode = document.createElement("DIV");
	fNewNode.setAttribute('id',  args.editorAreaId);
	LazyQMEditorContainer.appendChild(fNewNode);
    fNewNode = document.createElement("LINK");
    fNewNode.setAttribute('href',  Tcc.base +'js/tcc/qmeditor/style/comm.css?r=2');
    fNewNode.setAttribute('type', "text/css");
    fNewNode.setAttribute('rel', "stylesheet");
    LazyQMEditorContainer.appendChild(fNewNode);
    //init
    $.getScriptEx(Tcc.base + 'js/tcc/qmeditor/editor.js?r=16', function(){
        var qe = new qmEditor(args);
        //fix bug: can not bind submit on TT
        $('form').submit(function() {
            $('#' + args.id).val(qe.getContent());
        });
        qe.initialize(value, true, 1);
		qe.focus();
    $(document).trigger('qmEditorInit');
    });
}

/*
* lazy load rich editor
* author : franky
**/
Tcc.LazyRichEditor = function(args, loader_element) {
     args.needFocus = 1;
     if(!args.height)
        args.height = "260px";
    var LazyRichEditorContainer = document.getElementById('LazyRichEditorContainer');
    var fNewNode = document.createElement("INPUT");
    fNewNode.setAttribute('type', 'hidden');
    fNewNode.setAttribute('id',  args.id);
    fNewNode.setAttribute('name', args.name);
    fNewNode.setAttribute('richeditor', true);
    fNewNode.setAttribute('value', '');
    LazyRichEditorContainer.appendChild(fNewNode);
    fNewNode = document.createElement("LINK");
    fNewNode.setAttribute('href',  Tcc.base +'js/tcc/qqmaileditor/editor.css');
    fNewNode.setAttribute('type', "text/css");
    fNewNode.setAttribute('rel', "stylesheet");
    LazyRichEditorContainer.appendChild(fNewNode);
    fNewNode = document.createElement("DIV");
    fNewNode.innerHTML = '<iframe id="HtmlEditor" class="editor_frame" style="height:'+args.height+';" frameBorder="0" marginHeight=0 marginWidth=0 src="' + Tcc.base + 'js/tcc/qqmaileditor/blank.html' + '?domain=' + document.domain + '"></iframe>';
    LazyRichEditorContainer.appendChild(fNewNode);
    //init
    var _loadEditor = function() {$.getScriptEx(Tcc.base +'js/tcc/qqmaileditor.js?r=3', function(){initRichEditor(args); loader_element.parentNode.removeChild(loader_element); });};
    if (typeof window.jQuery.fn.offset == "undefined") {
        $.getScriptEx(Tcc.base +'js/jquery.dimensions.js', _loadEditor);
    } else {
        _loadEditor();
    }
};


/*
Tcc.WebPart = function(args) {
  if (typeof window.setHeight == "undefined") {
    document.write('<script type="text/javascript" src="' + Tcc.base + 'js/jquery.autoHeight.js' + '" />');
  }
  if (typeof jQuery.fn.offset == "undefined") {
    document.write('<script type="text/javascript" src="' + Tcc.base + 'js/query.dimensions.js' + '" />');
  }

  document.write('<div id="webpart_' + args.id + '<iframe id="webpart_frame_' + args.id + 'src="' + args.url + '" width="0" height="0" class="autoHeight" frameborder="0" scrolling="no"></iframe>';
  $('#webpart_frame_' + args.id).load(function() {
      var part = this.contentDocument.find('#' + args.id);
      $('#webpart_' + args.id).css('overflow', 'hidden').css('height', $(part).height()).css('margin-top', -$(part).offset().top);
    });
}
*/

Tcc.UserChooser.prototype = {
  //init a user chooser by given id
    initUserChooser: function(args) {
      var value = args.value ? args.value : '';
      var size = args.size ? args.size : '';
      var user_chooser_class = args.user_chooser_class ? args.user_chooser_class : 'txt-user-chooser';
      document.write('<input type="hidden" id="' + args.id + '" value="' + value + '" userchooser="true" name="' + args.name + '"/>');
      if (args.data_source_url) {
          //support user define data source url --joeyue
          if (args.inputType == 1) {
              document.write('<input type="text" id="' + args.id + 'Value" onfocus="_tcc_write_userscript(\'' + args.id + '\', \'' + args.choosertype + '\', \'' + args.data_source_url + '\', \'' + args.data_source_url_params + '\');" autocomplete="on" value="' + value + '" size="' + size + '" class="' + user_chooser_class+ '" />');
          } else if (args.inputType == 2) {
              document.write('<textarea id="' + args.id + 'Value" onfocus="_tcc_write_userscript(\'' + args.id + '\', \'' + args.choosertype + '\', \'' + args.data_source_url + '\', \'' + args.data_source_url_params + '\');" autocomplete="on" size="' + size +'" class="' + user_chooser_class + '">' + value + '</textarea>');
          }
      } else if (args.inputType == 1) {
          document.write('<input type="text" id="' + args.id + 'Value" onfocus="_tcc_write_userscript(\'' + args.id + '\', \'' + args.choosertype + '\');" autocomplete="on" value="' + value + '" size="' + size + '" class="' + user_chooser_class+ '" />');
      } else if (args.inputType == 2) {
          document.write('<textarea id="' + args.id + 'Value" onfocus="_tcc_write_userscript(\'' + args.id + '\', \'' + args.choosertype + '\');" autocomplete="on" size="' + size +'" class="' + user_chooser_class + '">' + value + '</textarea>');
      }
    }
};

function _tcc_write_userscript(clientid, choosertype){
    var sign = [0,0];
    var ctl = $("#" + clientid + "Value");
    var tmp_ctl_val = '';
    tmp_ctl_val = ctl.val();
     if(typeof(Actb)=='undefined'){
       disableCtl();
       $.getScriptEx(Tcc.base + 'js/tcc/userchooser.js?r=20110331', function(){sign[0] = 1;initChooser();});
     }
     else{
       sign[0] = 1;
     }

     var chooserdata = 'users';
     switch(choosertype) {
      case '3':
        chooserdata = 'usersandadgroups';
        break;
      case '2':
        chooserdata = 'adgroups';
        break;
      default:
        chooserdata = 'users';
        break;
     }

     if(typeof(eval('window._arr'+chooserdata))=='undefined'){
       disableCtl();
       if (arguments.length < 3) {
           $.getScriptEx(Tcc.base + 'js/' + chooserdata + '.js', function(){sign[1] = 1;initChooser();});
       } else {
           //use user data source
           var data_source_url = arguments[2];
           var data_source_url_params = arguments[3]? arguments[3] : '';
           $.getScriptEx(data_source_url + 'js/' + chooserdata + '.js' + data_source_url_params, function(){sign[1] = 1;initChooser();});
       }
     }
     else{
       sign[1] = 1;
     }

     if(sign[0] && sign[1]) {
       initChooser();
     }

     function initChooser(){
       if(!(sign[0] && sign[1]) || ctl.attr('init')) return;
       setChooser(eval('window._arr'+chooserdata), document.getElementById(clientid));
       sign[1] = 1;
       enableCtl();
     }


     function disableCtl(){
       if(ctl.attr('init') != 1){
         ctl.val('loading...');
         if (-[1,]) {
             //not IE
             ctl.css('color', '#9E9E9E');
             ctl.attr('readonly', true);
         } else {
             //IE
             ctl.attr('disabled', true);
         }
       }
     }

     function enableCtl(){
       if(sign[0] && sign[1]){
         ctl.attr('init', 1);
         ctl.val(tmp_ctl_val);
         if (-[1,]) {
             //not IE
             ctl.attr('readonly', false);
             ctl.css('color', '#000000');
         } else {
             //IE
             ctl.attr('disabled', false);
         }

         ctl.focus();
       }
     }
  }
