var cache = {},	lastXhr, city = null;

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