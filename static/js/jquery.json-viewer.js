/**
 * jQuery json-viewer
 * @author: Alexandre Bodelot <alexandre.bodelot@gmail.com>
 */
(function($){

  /**
   * Check if arg is either an array with at least 1 element, or a dict with at least 1 key
   * @return boolean
   */
  function isCollapsable(arg) {
    return arg instanceof Object && Object.keys(arg).length > 0;
  }

  /**
   * Check if a string represents a valid url
   * @return boolean
   */
  function isUrl(string) {
     var regexp = /^(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
     return regexp.test(string);
  }

  /**
   * Transform a json object into html representation
   * @return string
   */
  function json2html(json, options) {
    var html = '';
    if (typeof json === 'string') {
      /* Escape tags */
      json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      if (isUrl(json))
        html += '<a href="' + json + '" class="json-string">' + json + '</a>';
      else
        html += '<span class="json-string">"' + json + '"</span>';
    }
    else if (typeof json === 'number') {
      html += '<span class="json-literal">' + json + '</span>';
    }
    else if (typeof json === 'boolean') {
      html += '<span class="json-literal">' + json + '</span>';
    }
    else if (json === null) {
      html += '<span class="json-literal">null</span>';
    }
    else if (json instanceof Array) {
      if (json.length > 0) {
        html += '[<ol class="json-array">';
        for (var i = 0; i < json.length; ++i) {
          html += '<li>';
          /* Add toggle button if item is collapsable */
          if (isCollapsable(json[i])) {
            html += '<a href class="json-toggle"></a>';
          }
          html += json2html(json[i], options);
          /* Add comma if item is not last */
          if (i < json.length - 1) {
            html += ',';
          }
          html += '</li>';
        }
        html += '</ol>]';
      }
      else {
        html += '[]';
      }
    }
    else if (typeof json === 'object') {
      var key_count = Object.keys(json).length;
      if (key_count > 0) {
        html += '{<ul class="json-dict">';
        for (var key in json) {
          if (json.hasOwnProperty(key)) {
            html += '<li>';
            var keyRepr = options.withQuotes ?
              '<span class="json-string">"' + key + '"</span>' : key;
            /* Add toggle button if item is collapsable */
            if (isCollapsable(json[key])) {
              html += '<a href class="json-toggle">' + keyRepr + '</a>';
            }
            else {
              html += keyRepr;
            }
            html += ': ' + json2html(json[key], options);
            /* Add comma if item is not last */
            if (--key_count > 0)
              html += ',';
            html += '</li>';
          }
        }
        html += '</ul>}';
      }
      else {
        html += '{}';
      }
    }
    return html;
  }

  /**
   * jQuery plugin method
   * @param json: a javascript object
   * @param options: an optional options hash
   */
  $.fn.jsonViewer = function(json, options) {
    options = options || {};

    /* jQuery chaining */
    return this.each(function() {

      /* Transform to HTML */
      var html = json2html(json, options);
      if (isCollapsable(json))
        html = '<a href class="json-toggle"></a>' + html;

      /* Insert HTML in target DOM element */
      $(this).html(html);

      /* Bind click on toggle buttons */
      $(this).off('click');
      $(this).on('click', 'a.json-toggle', function() {
        var target = $(this).toggleClass('collapsed').siblings('ul.json-dict, ol.json-array');
        target.toggle();
        if (target.is(':visible')) {
          target.siblings('.json-placeholder').remove();
        }
        else {
          var count = target.children('li').length;
          var placeholder = count + (count > 1 ? ' items' : ' item');
          target.after('<a href class="json-placeholder">' + placeholder + '</a>');
        }
        return false;
      });

      /* Simulate click on toggle button when placeholder is clicked */
      $(this).on('click', 'a.json-placeholder', function() {
        $(this).siblings('a.json-toggle').click();
        return false;
      });

      if (options.collapsed == true) {
        /* Trigger click to collapse all nodes */
        $(this).find('a.json-toggle').click();
      }
    });
  };
})(jQuery);


//My code
//Radio button for json viewer
function selectForm() {
  $("div.json_source").hide();
  $("div.json-" + $("input:checked").val()).show();
}
selectForm();
$("input").click(function(){selectForm()});

//Render JSON from CDB
$(function() {
    $('#render_json_get').click(function() {
        $(this).prop('disabled', true);
		var tender_id = $("#form-view-json-get input[name=tender_id_long]").val();
		var api_version = $("#form-view-json-get select[name=api_version]").val();
		$.ajax({
            url: '/backend/jquery/get_tender_json/' + tender_id + '/' + api_version,
            type: 'GET',
            success: function(data) {
                console.log(data);
                $("#json_output").jsonViewer(data);
				$('#render_json_get').removeAttr("disabled");
			},
            error: function (jqXHR, textStatus, errorThrown) {
            	alert(jqXHR.status + ' ' + errorThrown + ': ' + jqXHR.responseText);
                $('#render_json_get').removeAttr("disabled");
            }
        });
    });
});

//Render JSON from form (input)
$(function() {
    $('#render_json_insert').click(function() {
        if(testJSON($('#raw_json_input').val()) === true){
			var raw_json = jQuery.parseJSON($('#raw_json_input').val());
			$("#json_output").jsonViewer(raw_json);
		}
		else {
			alert('Invalid JSON');
		}
    });
});



//Test if is JSON
function testJSON(input){
    try{
        JSON.parse(input);
        return true;
    }
    catch (error){
        return false;
    }
}