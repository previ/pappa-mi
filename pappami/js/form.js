function validateradio() {
	var value = false;
	var e = dojo.query('DIV.errorbox-bad');
	for(var x = 0; x < e.length; x++){e[x].setAttribute("class", "errorbox-good");}

	var radios = dojo.query('INPUT[type=radio]');
	var radio = radios[0];
	var first;
	for(var x = 0; x < radios.length; x++){
		//console.log(radio.name + radios[x].checked);
		if( radio.name != radios[x].name ) {
			if( value == false ) {
				var e = radio;
				while(e.getAttribute("class") != "errorbox-good" && e.getAttribute("class") != "errorbox-bad") e = e.parentNode;
				e.setAttribute("class", "errorbox-bad");
				if(first == undefined) first = radio;
			}
			value = false;
		}	
		radio = radios[x];
		value = value | radio.checked;
	}
	if( value == false ) {
		var e = radio;
		while(e.getAttribute("class") != "errorbox-good" && e.getAttribute("class") != "errorbox-bad") e = e.parentNode;
		e.setAttribute("class", "errorbox-bad");
		if(first == undefined) first = radio;
	}
	if(first) {
		first.focus()
		return false;
	}
	return true;
}

//Request the data using the query passed as a parameter
  var getMenu = function(){
    date = dojo.byId("e_dataIspezione").value;
    dateArr = date.split("/");
    date=dateArr[2]+"-"+dateArr[1]+"-"+dateArr[0];
    var urlserv = "/menu?cmd=getbydate&data="+date;

	var kw = {
	        url: urlserv,
	        load: function(data){ 
			var menu = data.split("|");				        	
	                dojo.byId('primoPrevisto').value = menu[0];
	                dojo.byId('secondoPrevisto').value = menu[1];
	                dojo.byId('contornoPrevisto').value = menu[2];
	                dojo.byId('primoEffettivo').value = menu[0];
	                dojo.byId('secondoEffettivo').value = menu[1];
	                dojo.byId('contornoEffettivo').value = menu[2];
	        },
	        error: function(data){
	                console.debug("Errore: ", data);
	        },
	        timeout: 2000
	};
	dojo.xhrGet(kw);
  }
  
function set_all(prefix, value) {
  var radios = dojo.query('INPUT[type=radio][name^='+prefix+'][value='+value+']');
  for(var x = 0; x < radios.length; x++){
    radios[x].checked = true;
  }	
}
