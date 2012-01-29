function init2() {
   
  // Create and populate the data table.
  var barOptsD = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#00FF00','#FFFF00','#FF0000']};
  var barOptsG = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#FF0000','#FFFF00','#00CC00','#00FF00']};
  var barOptsA = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#FF0000','#FFFF00','#00FF00']};
  var barOpts = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#FF0000','#FFFF00','#00FF00']};
  var barOptsC = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#0000FF','#00FF00','#FF0000']};
  var barOptsT = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#0000FF','#00FF00','#FF0000']};
  var barOptsQ = {width: 300, height: 100, isStacked: 'true', legend: 'none', colors: ['#FF0000','#00CC00','#00FF00']};
  
  //new google.visualization.ColumnChart(document.getElementById('cm_chart')).draw(cm_data, {width: 780, height: 410, is3D: true, title: 'Commissioni'});  
  new google.visualization.LineChart(document.getElementById('dati')).draw(dati_ins, {width: 780, height: 410, smoothLine: 'true', title: 'Dati raccolti', titleX: 'Settimane', curveType: "function"});  
  new google.visualization.ColumnChart(document.getElementById('aa_chart')).draw(aa_data, {width: 250, height: 100, legend: 'none', title: 'Aspetti ambientali'});  
  new google.visualization.PieChart(document.getElementById('nc_chart')).draw(nc_data, {width: 780, height: 410, legend: 'right', legendFontSize: '12', tooltipHeight: "120", tooltipFontSize: "14"});  

  new google.visualization.BarChart(document.getElementById('gg_chart')).draw(gg_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('zr_chart')).draw(zr_data, barOptsG);  
  new google.visualization.BarChart(document.getElementById('zc_chart')).draw(zc_data, barOptsG);  
  new google.visualization.BarChart(document.getElementById('sr_chart')).draw(sr_data, barOptsG);  
  new google.visualization.BarChart(document.getElementById('dp_chart')).draw(dp_data, barOptsD);  
  
  new google.visualization.BarChart(document.getElementById('pd_chart')).draw(pd_data, barOptsD);  
  new google.visualization.BarChart(document.getElementById('pc_chart')).draw(pc_data, barOptsC);  
  new google.visualization.BarChart(document.getElementById('pt_chart')).draw(pt_data, barOptsT);  
  new google.visualization.BarChart(document.getElementById('pq_chart')).draw(pq_data, barOptsQ);  
  new google.visualization.BarChart(document.getElementById('pa_chart')).draw(pa_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('pg_chart')).draw(pg_data, barOptsG);  

  new google.visualization.BarChart(document.getElementById('sd_chart')).draw(sd_data, barOptsD);  
  new google.visualization.BarChart(document.getElementById('sc_chart')).draw(sc_data, barOptsC);  
  new google.visualization.BarChart(document.getElementById('st_chart')).draw(st_data, barOptsT);  
  new google.visualization.BarChart(document.getElementById('sq_chart')).draw(sq_data, barOptsQ);  
  new google.visualization.BarChart(document.getElementById('sa_chart')).draw(sa_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('sg_chart')).draw(sg_data, barOptsG);  

  new google.visualization.BarChart(document.getElementById('cc_chart')).draw(cc_data, barOptsC);  
  new google.visualization.BarChart(document.getElementById('ct_chart')).draw(ct_data, barOptsT);  
  new google.visualization.BarChart(document.getElementById('cq_chart')).draw(cq_data, barOptsQ);  
  new google.visualization.BarChart(document.getElementById('ca_chart')).draw(ca_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('cg_chart')).draw(cg_data, barOptsG);  

  new google.visualization.BarChart(document.getElementById('bq_chart')).draw(bq_data, barOptsQ);  
  new google.visualization.BarChart(document.getElementById('ba_chart')).draw(ba_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('bg_chart')).draw(bg_data, barOptsG);  

  new google.visualization.BarChart(document.getElementById('fq_chart')).draw(fq_data, barOptsQ);  
  new google.visualization.BarChart(document.getElementById('fa_chart')).draw(fa_data, barOptsA);  
  new google.visualization.BarChart(document.getElementById('fm_chart')).draw(fm_data, barOptsC);  
  new google.visualization.BarChart(document.getElementById('fg_chart')).draw(fg_data, barOptsG);  
  $("#d_loading").hide();
  $("#statContainer").show();
}

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
 if($('#f_chgscope').is(':visible')) {
  $("#e_chgscope").popover('hide');
 } else {
  $("#e_chgscope").popover('show');

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
}
