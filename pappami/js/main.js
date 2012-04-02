"use strict";

var cache = {},	lastXhr, city = null;
var combo_config = {
  'navi_simple' : true,
  'lang'        : 'it',
  'sub_info'    : false,
  'select_only' : true,
  'primary_key' : 'value',
  'bind_to'	: 'selected',
  'field'	: 'label',
  'db_table'    : 'citta',
  'button_img'  : '/img/combobox_button.png',
  'load_img'    : '/img/ajax-loader.gif'
}

var init_value = "";

function oncitychanged() {
  combo_config['init_val'] = init_value;
  if( $("#citta").val() != "" && $("#citta").val() != city) {
    if( !cache[$("#citta").val()] ) {
      var query = { 'city': $("#citta").val() }
      lastXhr = $.getJSON( "/profilo/getcm", query, function( data, status, xhr ) {
	city = $("#citta").val()
	cache[city] = data
	$('#commissione_sel').parent().html('<input class="" id="commissione_sel" name="commissione_sel" value="{{ctx.cm_name}}"/><input type="hidden" id="cm" name="cm" value=""/>');
	$('#commissione_sel').ajaxComboBox(data, combo_config).bind("selected", function(event, ui) { 
	  $("#cm").val($("#commissione_sel_hidden").val()); 
	}); 	
      });    
    } else {
      city = $("#citta").val()
      $('#commissione_sel').parent().html('<input class="" id="commissione_sel" name="commissione_sel" value="{{ctx.cm_name}}"/><input type="hidden" id="cm" name="cm" value=""/>');
      $('#commissione_sel').ajaxComboBox(cache[city], combo_config).bind("selected", function(event, ui) { 
	  $("#cm").val($("#commissione_sel_hidden").val()); 
	});
    }
  }
}
/*
function getCommissioniFromCache(term) {
  found = Array();
  for(c in cache) {	
    if(term.toUpperCase() == c.substring(0,term.length).toUpperCase()) {
      found.push({"label": c, "value": cache[c]});
    }
  }
  return found;
}

function chgscope() {
  $("#commissione_sel").autocomplete({
    minLength: 2,
    source: function( request, response ) {
      var term = request.term;
      request.city = $("#citta").val();
      if ( city == null || city != $("#citta").val() ) {
	cache = {};
	lastXhr = $.getJSON( "/profilo/getcm", request, function( data, status, xhr ) {
	  items = data;
	  for (item in items) {
	    cache[items[item]["label"]] = items[item]["value"];
	  }
	  city = $("#citta").val();
	  response(getCommissioniFromCache(term));
	});
      } else {
	response(getCommissioniFromCache(term));
      }
    },
    select: function(event, ui) { 
      $("#commissione").val(ui.item.value);
      ui.item.value= ui.item.label;
    } 
  });    
}
*/