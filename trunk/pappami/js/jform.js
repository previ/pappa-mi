var getMenu = function(){  
  date = $("#e_dataIspezione").val();
  commissione = $("#e_commissione").val();
  if(date && commissione) {
    //dateArr = date.split("/");
    //date=dateArr[2]+"-"+dateArr[1]+"-"+dateArr[0];
    $.ajax({url:"/menu?cmd=getbydate&data="+date+"&commissione="+commissione, success:function(data){ 
	var menu = data.split("|");				        	
	$('#e_primoPrevisto').val(menu[0]);
	$('#e_secondoPrevisto').val(menu[1]);
	$('#e_contornoPrevisto').val(menu[2]);
	$('#e_primoEffettivo').val(menu[0]);
	$('#e_secondoEffettivo').val(menu[1]);
	$('#e_contornoEffettivo').val( menu[2]);	
	onMenuChanged();
    }});
  }
}

function onMenuChanged() {
      if($("#e_primoEffettivo").val() != "" && $("#e_primoEffettivo").val() == $("#e_secondoEffettivo").val() ) {
	      oldDisp_1 = $('#s_secondo_1').css('display');
	      oldDisp_2 = $('#s_secondo_2').css('display');
	      oldDisp_3 = $('#s_secondo_3').css('display');
	      //$('#s_secondo_1').css('display', "none");
	      //$('#s_secondo_2').css('display', "none");
	      //$('#s_secondo_3').css('display', "none");
	      piattounico = true;
	      $('#tab_primo').text("Piatto unico");
	      $('#tab_secondo').parent().hide();
	      $('#s_primo').html($('#e_primoEffettivo').val());
	      $('#step3next').val('step5');
      } else {
	      //$('#s_secondo_1').css('display', oldDisp_1);
	      //$('#s_secondo_2').css('display', oldDisp_2);
	      //$('#s_secondo_3').css('display', oldDisp_3);
	      piattounico = false;
	      $('#tab_primo').text("Primo");
	      $('#tab_secondo').parent().show();
	      $('#s_primo').text($('#e_primoEffettivo').val());
	      $('#s_secondo').text($('#e_secondoEffettivo').val());
	      $('#step3next').val('step4');
      }
      $('#s_contorno').text("Contorno: " + $('#e_contornoEffettivo').val());
}

function getPrevIspData() {
  getMenu();
  commissione = $("#e_commissione").attr("value");

  if(($('[name="aaRispettoCapitolato"]')[0].checked != 
      $('[name="aaRispettoCapitolato"]')[1].checked ) && 
      commissione &&
      !window.confirm("Caricare i dati 'ambientali' da precedente scheda inserita per la Commissione ?") ) {
     return;
  }

  $.ajax({url:"/isp/getispdata?cm="+commissione, success: function(data){ 
	var ispdata = data.split("|");
	if(ispdata.length > 1) {
	  $('[name="aaRispettoCapitolato"]')[0].checked = ispdata[0] == 1;
	  $('[name="aaRispettoCapitolato"]')[1].checked = ispdata[0] == 0;
	  $('[name="aaTavoliApparecchiati"]')[0].checked = ispdata[1] == 1;
	  $('[name="aaTavoliApparecchiati"]')[1].checked = ispdata[1] == 0;
	  $('[name="aaTermichePulite"]')[0].checked = ispdata[2] == 1;
	  $('[name="aaTermichePulite"]')[1].checked = ispdata[2] == 0;
	  $('[name="aaAcqua"]')[0].checked = ispdata[3] == 1;
	  $('[name="aaAcqua"]')[1].checked = ispdata[3] == 0;
	  $('[name="aaScaldaVivande"]')[0].checked = ispdata[4] == 1;
	  $('[name="aaScaldaVivande"]')[1].checked = ispdata[4] == 0;
	  $('[name="aaSelfService"]')[0].checked = ispdata[5] == 1;
	  $('[name="aaSelfService"]')[1].checked = ispdata[5] == 0;
	  $('[name="aaTabellaEsposta"]')[0].checked = ispdata[6] == 1;
	  $('[name="aaTabellaEsposta"]')[1].checked = ispdata[6] == 0;
	  $('[name="ricicloStoviglie"]')[0].checked = ispdata[7] == 1;
	  $('[name="ricicloStoviglie"]')[1].checked = ispdata[7] == 0;
	  $('[name="ricicloPosate"]')[0].checked = ispdata[8] == 1;
	  $('[name="ricicloPosate"]')[1].checked = ispdata[8] == 0;
	  $('[name="ricicloBicchieri"]')[0].checked = ispdata[9] == 1;
	  $('[name="ricicloBicchieri"]')[1].checked = ispdata[9] == 0;
	  $('#step2').updateRadioState();
	}
	}
	});
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
