"use strict";

var getMenu = function(){  
  var date = $("#e_dataIspezione").val();
  var commissione = $("#e_commissione").val();
  if(date && commissione) {
    //dateArr = date.split("/");
    //date=dateArr[2]+"-"+dateArr[1]+"-"+dateArr[0];
    $.ajax({url:"/menu?cmd=getbydate&data="+date+"&commissione="+commissione, success:function(data){     
	var menu = eval("("+data+")");		
	if( menu["primo"] ) {
	  $('#e_primoPrevisto').attr('readonly', true);
	  $('#e_secondoPrevisto').attr('readonly', true);
	  $('#e_contornoPrevisto').attr('readonly', true);
	  $('#e_primoPrevisto').removeClass('required');
	  $('#e_secondoPrevisto').removeClass('required');
	  $('#e_contornoPrevisto').removeClass('required');	  
	  $('#e_primoPrevisto').val(menu["primo"]);
	  $('#e_secondoPrevisto').val(menu["secondo"]);
	  $('#e_contornoPrevisto').val(menu["contorno"]);
	  $('#e_primoEffettivo').val(menu["primo"]);
	  $('#e_secondoEffettivo').val(menu["secondo"]);
	  $('#e_contornoEffettivo').val( menu["contorno"]);	
	  $('#e_primoPiattoEffettivo').val(menu["primo_key"]);
	  $('#e_secondoPiattoEffettivo').val(menu["secondo_key"]);
	  $('#e_contornoPiattoEffettivo').val( menu["contorno_key"]);	
	  onMenuChanged();
	} else {
	  $('#e_primoPrevisto').attr('readonly', false);
	  $('#e_secondoPrevisto').attr('readonly', false);
	  $('#e_contornoPrevisto').attr('readonly', false);
	  $('#e_primoPrevisto').addClass('required');
	  $('#e_secondoPrevisto').addClass('required');
	  $('#e_contornoPrevisto').addClass('required');
	  $('#e_primoPrevisto').change(function () {$('#e_primoEffettivo').val($('#e_primoPrevisto').val());});
	  $('#e_secondoPrevisto').change(function () {$('#e_secondoEffettivo').val($('#e_secondoPrevisto').val());});
	  $('#e_contornoPrevisto').change(function () {$('#e_contornoEffettivo').val($('#e_contornoPrevisto').val());});
	}
    }});
  }
}

function onMenuChanged() {
      if($("#e_primoEffettivo").val() != "" && $("#e_primoEffettivo").val() == $("#e_secondoEffettivo").val() ) {
	      var oldDisp_1 = $('#s_secondo_1').css('display');
	      var oldDisp_2 = $('#s_secondo_2').css('display');
	      var oldDisp_3 = $('#s_secondo_3').css('display');
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
      $('#s_contorno').text($('#e_contornoEffettivo').val());
      $("#form0").find("#e_submit").removeAttr("disabled"); 

}

function getPrevIspData() {
  $("#form0").find("#e_submit").attr("disabled", true); 
  getMenu();
  var commissione = $("#e_commissione").attr("value");

  if(($('[name="aaRispettoCapitolato"]')[0].checked != 
      $('[name="aaRispettoCapitolato"]')[1].checked ) && 
      commissione &&
      !window.confirm("Caricare i dati 'ambientali' da precedente scheda inserita per la Commissione ?") ) {
     return;
  }

  $.ajax({url:"/isp/getispdata?cm="+commissione, success: function(data){ 
    var ispdata = data.split("|");
      if(ispdata.length > 1) {
	$($('[name="aaRispettoCapitolato"]')[ispdata[0]==0 ? 1 : 0]).parent().click();	
	$($('[name="aaRispettoCapitolato"]')[ispdata[0]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaTavoliApparecchiati"]')[ispdata[1]==0 ? 1 : 0]).parent().click();
	$($('[name="aaTavoliApparecchiati"]')[ispdata[1]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaTermichePulite"]')[ispdata[2]==0 ? 1 : 0]).parent().click();	
	$($('[name="aaTermichePulite"]')[ispdata[2]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaAcqua"]')[ispdata[3]==0 ? 1 : 0]).parent().click();
	$($('[name="aaAcqua"]')[ispdata[3]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaScaldaVivande"]')[ispdata[4]==0 ? 1 : 0]).parent().click();
	$($('[name="aaScaldaVivande"]')[ispdata[4]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaSelfService"]')[ispdata[5]==0 ? 1 : 0]).parent().click();	  
	$($('[name="aaSelfService"]')[ispdata[5]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="aaTabellaEsposta"]')[ispdata[6]==0 ? 1 : 0]).parent().click();
	$($('[name="aaTabellaEsposta"]')[ispdata[6]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="ricicloStoviglie"]')[ispdata[7]==0 ? 1 : 0]).parent().click();	
	$($('[name="ricicloStoviglie"]')[ispdata[7]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="ricicloPosate"]')[ispdata[8]==0 ? 1 : 0]).parent().click();	
	$($('[name="ricicloPosate"]')[ispdata[8]==0 ? 1 : 0]).attr('checked', true)
	$($('[name="ricicloBicchieri"]')[ispdata[9]==0 ? 1 : 0]).parent().click();
	$($('[name="ricicloBicchieri"]')[ispdata[9]==0 ? 1 : 0]).attr('checked', true)
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
