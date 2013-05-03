$("#page-menu").bind('pageinit', function(event, entry) {
  //$("page-menu").find('span[data-v-title]').text("Pappa Mi");    

  veespo.ready(function(){

    $.ajax({url:"/api/getuser", 
	    dataType:'json',
	    success:function(data) { 

      userpappami = data;
      now = new Date()
      initUI(userpappami, userpappami.schools[0].id, getPrevBizDay(new Date(now.getFullYear(), now.getMonth(), now.getDate())));
      
      $('#user').text(userpappami.fullname);
      veespo.set.group("group-pappa-mi");
      veespo.set.lang("it");
      veespo.set.userId("uid-" + userpappami.id);
      veespo.set.userName(userpappami.fullname);

    }});    
  });
 
});

function getPrevBizDay(date) {
  var dt = date;
  while(dt.getDay()>5 || dt.getDay()==0) {
    dt = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()-1)
  }
  return dt;
}

function getNextBizDay(date) {
  var dt = date;
  while(dt.getDay()>5 || dt.getDay()==0) {
    dt = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()+1)
  }
  return dt;
}

function getDateFromStr(date_str) {
  date_v = date_str.split("-");
  date = new Date(date_v[0], date_v[1]-1, date_v[2]);
  return date;
}

$(document).bind( "pageloadfailed", function( event, data ){

	// Let the framework know we're going to handle things.
	event.preventDefault();

	window.location.href="/eauth/login?next="+data.absUrl;
	//$.mobile.changePage("#page-login");
	data.deferred.reject( data.absUrl, data.options );
});  
 
$("#page-menu").bind('swipeleft', function(event) {
  $.mobile.showPageLoadingMsg();
  var cur_date = $('#data');    
  var cur_sk = $('#cm').find("option[selected]='true'");    
  date = getDateFromStr(cur_date.attr("value"));
  next_date = getNextBizDay(new Date(date.getFullYear(), date.getMonth(), date.getDate()+1));  
  if(next_date) initUI(userpappami, cur_sk.attr("value").substring("sk-pappa-mi-".length), next_date);
});
  
$("#page-menu").bind('swiperight', function(event) {
  $.mobile.showPageLoadingMsg();
  var cur_date = $('#data');    
  var cur_sk = $('#cm');    
  date = getDateFromStr(cur_date.attr("value"));
  next_date = getPrevBizDay(new Date(date.getFullYear(), date.getMonth(), date.getDate()-1));  
  if(next_date) initUI(userpappami, cur_sk.attr("value").substring("sk-pappa-mi-".length), next_date);
});

$("#page-menu").bind('pagebeforeshow', function(event){ 
  console.log("Schools page...");
  /*$("#page-menu").find('span[data-v-title]').text(userpappami.fullname);
  if (pappami.resetMenu){
    //entry.refs.menuAnc.empty();
  } else {*/
    var lrt = veespo.get.lastSavedTargetId();
    $("#page-menu").find('span[data-role]="button"').each(function(){
      var e = $(this);
      var id = mutils.geu(e, "data-veespo-id", "att");
      if (id == lrt){
	console.log("setting data icon for: " + lrt);
	e.find(".ui-icon").addClass("ui-icon-check").removeClass("ui-icon-plus");
      }
    });
  //}  
}); 

var back = function(){
  $.mobile.changePage("#page-menu");
  return false;
};

function initUI(userpappami, sk, dt) {
  var params = $('<fieldset id="params" data-role="controlgroup" data-type="vertical"><select id="cm" name="school" data-mini="true" data-native-menu="false"/><select id="data" name="cm" data-mini="true" data-native-menu="false"/></fieldset>');
  //var params = $('<select id="cm" name="school" data-mini="true" data-native-menu="true"/><div data-role="controlgroup" data-type="horizontal"><a href="#" data-role="button" data-mini="true" data-inline="true" data-icon="arrow-l">&nbsp</a><select id="data" name="data" data-role="button" data-mini="true" data-inline="true" data-native-menu="true"/><a href="#" data-inline="true" data-mini="true" data-role="button" data-icon="arrow-r" data-iconpos="right">&nbsp</a></div>');
  var sel_sk = params.find("#cm");
  var sel_date = params.find("#data");
  
  for( school in userpappami.schools) {
    sel_sk.append( $("<option>").attr("value", "sk-pappa-mi-" + userpappami.schools[school].id).text(userpappami.schools[school].name));
  }     
  sel_sk.find("option[value='" + "sk-pappa-mi-" + sk + "']").attr("selected",1);
  
  for( i=-7;i<=7;i++) {
   date = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()-i);

   if(date.getDay()<6 && date.getDay()>0) {
    var d = $("<option>");
    if(date.getTime() == dt.getTime()){      
      d.attr("selected",1);
    }
    sel_date.append( d.attr("value", date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate()).text(date.toLocaleDateString("it")));
   }
  }
  
  $('#page-menu').find('[data-role="content"]').html(params).trigger("create");
  
  sel_date.change( loadMenu );
  sel_sk.change( loadMenu );
  
  sel_date.trigger("change");
}

var menu = {};
function loadMenu() {
  
  var date = $('#data').val(); 
  var cm = $('#cm').val();
  var params = {'date': date, 'school': cm.substring("sk-pappa-mi-".length) };
  
  var date_d = getDateFromStr(date);
  var today = getPrevBizDay(new Date());
  
  $.ajax({url:"/api/getmenu",
	data: params,
	dataType:'json',
	success:function(data) { 
    menu = data;
  
    var list = [];
    for (var k in menu){
      list.push(menu[k]);
    };
  
    var template = '';
    template += '<table class="pappa-mi-menu">';
    template += '{{#list}}'; 
    template += '<tr data-veespo-id="demo-pappa-mi-{{id}}">';
    template += '<td class="left">{{desc1}}</td>';
    
    if(today.getTime() >= date_d.getTime()) {
      template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right">Vota</span></td>';
    } else {
      template += '<td class="right"><span data-role="button" data-mini="true" data-icon="plus" data-iconpos="right" class="ui-disabled">Vota</span></td>';
    }
    template += '</tr>';
    template += '{{/list}}'; 
    template += '</table>';
  
    var html = $(Mustache.to_html(template, {list:list} ));
    $('#menu').html($(html)).trigger("create");
    
    $.mobile.hidePageLoadingMsg();
       
    $('#menu').find('span[data-role]="button"').bind('tap', function(evt){
      var e  = mutils.event.elem(evt);
      var id = mutils.geu(e, "data-veespo-id", "att");
      var title = getDish(id.substring('demo-pappa-mi-'.length)).desc1;
      veespo.set.target(id, "group-pappa-mi", title);
      veespo.display(back,back);
    });
  }});
}

/*
 * Torna l'oggetto relativo al id del piatto passato
 */
function getDish(id){
  for(dish in menu) {
    if(menu[dish].id == id){
      return menu[dish];
    }
  }
  throw(new Error("Failed to find dish: " + id));
};
