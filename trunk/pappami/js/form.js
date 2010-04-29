function validateradio() {
	var value = false;
	var e = dojo.query('DIV.errorbox-bad');
	for(var x = 0; x < e.length; x++){e[x].setAttribute("className", "errorbox-good");}

	var radios = dojo.query('INPUT[type=radio]');
	var radio = radios[0];
	var first;
	for(var x = 0; x < radios.length; x++){
		console.log(radio.name + radios[x].checked);
		if( radio.name != radios[x].name ) {
			if( value == false ) {
				var e = radio;
				while(e.className != "errorbox-good" && 
				      e.className != "errorbox-bad" && 
				      e.parentNode) {
				      e = e.parentNode;
				}
				e.setAttribute("class", "errorbox-bad");
				e.setAttribute("className", "errorbox-bad");
				if(first == undefined) first = radio;
			}
			value = false;
		}	
		radio = radios[x];
		value = value | radio.checked;
	}
	if( value == false ) {
		var e = radio;
		while(e.className != "errorbox-good" && e.className != "errorbox-bad") e = e.parentNode;
		e.setAttribute("class", "errorbox-bad");
		e.setAttribute("className", "errorbox-bad");
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
    commissione = dojo.byId("e_commissione").value;
    dateArr = date.split("/");
    date=dateArr[2]+"-"+dateArr[1]+"-"+dateArr[0];
    var urlserv = "/menu?cmd=getbydate&data="+date+"&commissione="+commissione;
	var kw = {
	        url: urlserv,
	        load: function(data){ 
			var menu = data.split("|");				        	
	                dojo.byId('e_primoPrevisto').value = menu[0];
	                dojo.byId('e_secondoPrevisto').value = menu[1];
	                dojo.byId('e_contornoPrevisto').value = menu[2];
	                dojo.byId('e_primoEffettivo').value = menu[0];
	                dojo.byId('e_secondoEffettivo').value = menu[1];
	                dojo.byId('e_contornoEffettivo').value = menu[2];
	        },
	        error: function(data){
	                console.debug("Errore: ", data);
	        },
	        timeout: 2000
	};
	dojo.xhrGet(kw);
  }
  
function setAll(prefix, value) {
  var radios = dojo.query('INPUT[type=radio][name^='+prefix+']');
  for(var x = 0; x < radios.length; x++){
    var radio = radios[x];
    if(radio.name!="ncPresenti") {
      if(value=="0") {
        if(radio.value=="0")        
          radio.checked = true;
	else
	  radio.checked = false;
        radio.disabled = true;
      } else {
        radio.disabled = false;
      }
    }
  }	
}
function enableAll(prefix) {
  var radios = dojo.query('INPUT[type=radio][name^='+prefix+']');
  for(var x = 0; x < radios.length; x++){
    var radio = radios[x];
    if(radio.name!="ncPresenti") {
      radio.disabled = false;
    }
  }	
}
function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}