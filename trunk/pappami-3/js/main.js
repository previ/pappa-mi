"use strict";

var cache = {},	lastXhr, city = null;
var combo_config = {
  'navi_simple' : true,
  'lang'        : 'it',
  'select_only' : true,
  'primary_key' : 'value',
  'bind_to'	: 'selected',
  'field'	: 'label',
  'db_table'    : 'citta',
  'button_img'  : '/img/combobox_button.png',
  'load_img'    : '/img/ajax-loader.gif',
  'sub_info'    : false
}

var init_value = "";

function oncitychanged() {
  combo_config['init_record'] = init_value;
  if( $("#citta").val() != "" && $("#citta").val() != city) {
    if( !cache[$("#citta").val()] ) {
      var query = { 'city': $("#citta").val() }
      lastXhr = $.getJSON( "/profilo/getcm", query, function( data, status, xhr ) {
	city = $("#citta").val()
	cache[city] = data
	$('#commissione_sel').parent().html('<input class="" id="commissione_sel" name="commissione_sel"/><input type="hidden" id="cm" name="cm" value=""/>');
	$('#commissione_sel').ajaxComboBox(data, combo_config).bind("selected", function(event, ui) { 
	  $("#cm").val($("#commissione_sel_hidden").val()); 
	}); 	
      });    
    } else {
      city = $("#citta").val()
      $('#commissione_sel').parent().html('<input class="" id="commissione_sel" name="commissione_sel"/><input type="hidden" id="cm" name="cm" value=""/>');
      $('#commissione_sel').ajaxComboBox(cache[city], combo_config).bind("selected", function(event, ui) { 
	  $("#cm").val($("#commissione_sel_hidden").val()); 
	});
    }
  }
}

function showDishDetails(event) {
  if(!isVisible){
    var target = $(event.target);
    var params = {'cmd': 'getdetails', 'piatto': target.attr("data-detail-key"), 'cm': target.attr("data-detail-cm")};
    $.ajax({url:"/menu", 
	    data: params,
	    dataType:'json',
	    success:function(data) { 
      var html = '<h5>'+data.piatto+'</h5><ul class=\'unstyled\'>';
      html += '<li><spam>Ingrediente</span><span style=\'float:right;\'>g.</span></li>';
      for( var i in data.ingredienti) {
	html += '<li><spam>' + data.ingredienti[i].nome + '</span><span style=\'float:right;\'>' + Math.round(data.ingredienti[i].quantita*10)/10; + '</span></li>';
      }
      html += '</ul>';
      target.attr('data-content', html);    
      target.popover('show');
      isVisible = true
      event.preventDefault()
    }});
  }
}

$.pnotify.defaults.delay = 5000;