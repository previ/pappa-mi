
$("#page-init").bind('pagecreate', function(event, entry){
  
  $("#page-init").find('span[data-v-title]').text("Pappa-Mi");
  
  //pappami.uid = mutils.cookie.get("m-pappa-mi-uid") || "uid-pappa-mi-0";
  //pappami.resetMenu = true;
  
  $.mobile.changePage('#page-menu', {changeHash: true, transition: 'fade'});

  //entry.refs.content.html('<a data-role="button" href="/mobile#page-menu">Leggi e vota il Menù</a>');
 
  /*
  var list = $('<select data-native-menu="false">').change(
      function(evt){
        var e = mutils.event.elem(evt);
        pappami.uid = e.val();
        mutils.cookie.set("m-pappa-mi-uid", pappami.uid);
        pappami.resetMenu = true;
        if (veespo.ready() && pappami.uid != "uid-pappa-mi-0"){
          entry.refs.btn.removeClass('ui-disabled'); 
        } else {
          entry.refs.btn.addClass('ui-disabled');  
        }
    });
  for (var uid in pappami.td.users){
    list.append( $("<option>").attr("value", uid).text(pappami.td.users[uid]));
  }
  
  list.find("option[value='" + pappami.uid + "']").attr("selected",1);
  entry.refs.content.append(list);  
  entry.refs.btn = $('<span style="width:100px" data-theme="e" sdata-icon="check" data-role="button">Load</span>').bind('tap', function(){
    veespo.set.userId(pappami.uid);
    veespo.set.userName(pappami.td.users[pappami.uid]);
    $.mobile.changePage('#page-menu', {changeHash: true, transition: 'fade'});  
  });
  
  entry.refs.footer.find("span").replaceWith(entry.refs.btn);
  entry.refs.btn.addClass('ui-disabled');  
  veespo.ready(function(){
    veespo.set.group("group-pappa-mi");
    veespo.set.lang("it");
    if (pappami.uid != "uid-pappa-mi-0"){
      entry.refs.btn.removeClass('ui-disabled');  
    }
  });
*/  
});
/*
veespo.templates.add( 'p-pappa-mi-init' , 'pagebeforeshow', function(event, entry){
 console.log("Init page...");
});
*/

