/*
 * Questo script emula le chiamate all'api di pappa-mi 
 */

window.pappami = window.pappami || {};
window.pappami.td = {};

/*
 * Genera in maniera casuale un menu composto da primo, secondo, contorno e dolce
 */
window.pappami.td.getMenu = function(){
  var getIndex = function(type){
    var start = -1; 
    var end;
    for (var i=0; i<pappami.td.piatti.length; i++){
      if (pappami.td.piatti[i].desc2 == type){
        if (start == -1){
          start = i;
        } else {
          end = i;
        }
      }
    }
    var index = Math.floor(Math.random() * (1 + end - start)) + start;
    console.log(type, index);
    return index;
  };
  return {
    "primo"    : pappami.td.piatti[getIndex("primo")],
    "secondo"  : pappami.td.piatti[getIndex("secondo")],
    "contorno" : pappami.td.piatti[getIndex("contorno")],
    "dolce"    : pappami.td.piatti[getIndex("dolce-frutta")],
  };
};

/*
 * Torna l'oggetto relativo al id del piatto passato
 */
window.pappami.td.getDish = function(id){
  for (var i=0; i<pappami.td.piatti.length; i++){
    if (pappami.td.piatti[i].id == id){
      return pappami.td.piatti[i];
    }
  }
  throw(new Error("Failed to find dish: " + id));
};

/*
 * Puoi cambiare i nomi, ma meglio non cambiare gli uid
 */
/* 
$.ajax({url:"/api/getuser", 
	dataType:'json',
	success:function(data) { 
 var userpappami = data;
 alert("user: " + userpappami.id);
 var user = {"uid-pappa-mi-0"  : "Scegli"};
 user["uid-pappa-mi-" + "1"] = userpappami.fullname;
 window.pappami.td.users = user;
 alert("user: " + JSON.stringify(window.pappami.td.users));
 var scuole = {};
 var schools = userpappami.schools;
 
 for( school in schools) {
   scuole["sk-pappa-mi-"+school.id] = school.name;
 }
 window.pappami.td.scuole = scuole;
 
}});
*/

/*
window.pappami.td.users = {
  "uid-pappa-mi-0"  : "Scegli",  
  "uid-pappa-mi-1"  : "Aldo Altobelli",  
  "uid-pappa-mi-2"  : "Bruno Bellissimo",  
  "uid-pappa-mi-3"  : "Carlo Ciampi",  
  "uid-pappa-mi-4"  : "Davide Danese",  
  "uid-pappa-mi-5"  : "Emanuele Emanuele",  
  "uid-pappa-mi-6"  : "Francesca Fattini",  
  "uid-pappa-mi-7"  : "Georgia Grimaldi",  
  "uid-pappa-mi-8"  : "Izabella Initini",  
  "uid-pappa-mi-9"  : "Lettizia Littizzetto",  
  "uid-pappa-mi-10" : "Manuela Martelli",  
};
*/
/*
 * Qui puoi cambiare quello che vuoi
 */

/*
window.pappami.td.scuole = {
  "sk-pappa-mi-0" : "Scegli Scuola",
  "sk-pappa-mi-1" : "Scuola-1",
  "sk-pappa-mi-2" : "Scuola-2",
  "sk-pappa-mi-3" : "Scuola-3",
  "sk-pappa-mi-4" : "Scuola-4",
  "sk-pappa-mi-5" : "Scuola-5",
  "sk-pappa-mi-6" : "Scuola-6",
  "sk-pappa-mi-7" : "Scuola-7",
  "sk-pappa-mi-8" : "Scuola-8",
  "sk-pappa-mi-9" : "Scuola-9",
};
*/
/*
 * Qui puoi cambiare quello che vuoi
 * Io ho messo solo i giorni, ma qui ci vorranò le date vere
 */
/*
function initDates() {
 var dates = {"data-pappa-mi-0" : "Scegli Giorno"};
 now = new Date();
 for( i=0;i<=7;i++) {
  date = new Date(now.getFullYear(), now.getMonth(), now.getDate()-i);
  if(date.getDay()<6 && date.getDay()>0) {
   dates["data-pappa-mi-" + date.toJSON()]=date.toLocaleDateString();
  }
 }
 return dates;
}
window.pappami.td.date = initDates();
*/
/*
window.pappami.td.date = {
  "data-pappa-mi-0" : "Scegli Giorno",
  "data-pappa-mi-1" : "Lunedì",
  "data-pappa-mi-2" : "Martedì",
  "data-pappa-mi-3" : "Mercoledì",
  "data-pappa-mi-4" : "Giovedì",
  "data-pappa-mi-5" : "Venerdì",
};
*/
/*
 * Qui non cambiare nulla
 * E' un copia-incolla dei dati sul nostro server
 * Potremmo anche scaricarli direttamente ...
 */
window.pappami.td.piatti = [
   {id:    "demo-pappa-mi-1",
    desc1: "Pasta al pomodoro",
    desc2: "primo"},
   {id:    "demo-pappa-mi-2",
    desc1: "Pasta al pesto",
    desc2: "primo"},
   {id:    "demo-pappa-mi-3",
    desc1: "Tortellini in brodo",
    desc2: "primo"},
   {id:    "demo-pappa-mi-4",
    desc1: "Riso alle zucchine",
    desc2: "primo"},
   {id:    "demo-pappa-mi-5",
    desc1: "Riso al parmeggiano",
    desc2: "primo"},
    
   {id:    "demo-pappa-mi-6",
    desc1: "Fesa di tacchino al forno",
    desc2: "secondo"},
   {id:    "demo-pappa-mi-7",
    desc1: "Cotoletta alla Milanese",
    desc2: "secondo"},
   {id:    "demo-pappa-mi-8",
    desc1: "Pollo al forno",
    desc2: "secondo"},
   {id:    "demo-pappa-mi-9",
    desc1: "Pesce lessato",
    desc2: "secondo"},
   {id:    "demo-pappa-mi-10",
    desc1: "Hamburger",
    desc2: "secondo"},
   {id:    "demo-pappa-mi-11",
    desc1: "Frittata alle verdure",
    desc2: "secondo"},
    
   {id:    "demo-pappa-mi-12",
    desc1: "Verdura Lessa",
    desc2: "contorno"},
   {id:    "demo-pappa-mi-13",
    desc1: "Verdura alla Piastra",
    desc2: "contorno"},   
   {id:    "demo-pappa-mi-14",
    desc1: "Patate Fritte",
    desc2: "contorno"},              
   {id:    "demo-pappa-mi-15",
    desc1: "Insalata Mista",
    desc2: "contorno"}, 

    {id:    "demo-pappa-mi-16",
     desc1: "Gelato",
     desc2: "dolce-frutta"},
    {id:    "demo-pappa-mi-17",
     desc1: "Millefoglie",
     desc2: "dolce-frutta"},   
    {id:    "demo-pappa-mi-18",
     desc1: "Torta al limone",
     desc2: "dolce-frutta"},              
    {id:    "demo-pappa-mi-19",
     desc1: "Uva",
     desc2: "dolce-frutta"},                
 ];
