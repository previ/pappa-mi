var tour = new Tour({
    labels: {
        next: "Avanti »",
        prev: "« Indietro",
        end: "Fine"
    }});

tour.addStep({
    element: ".s_node_panel", // string (jQuery selector) - html element next to which the step popover should be shown
    title: "Argomenti", // string - title of the popover
    content: "<p>Tutti i dati sono pubblicati su un <strong>Argomento</strong>.</p><p>Un Argomento è come un raccoglitore di messaggi.</p><p>Sono Argomenti le Scuole, le Città e naturalmente gli argomenti in ambito all'alimentazione scolastica.", // string - content of the popover
    backdrop: false 
});

tour.addStep({
    element: ".s_node_panel [data-node-key='all']",
    title: "Seleziona argomento",
    content: "Questo link mostra <strong>tutti i messaggi degli argomenti a cui sei iscritto</strong>.",
    backdrop: false,
    placement: "right"
});

tour.addStep({
    element: ".s_node_panel [data-node-key='news']",
    title: "Seleziona argomento",
    content: "Mentre questo link mostra <strong>tutti i messaggi più recenti</strong>, anche di argomenti a cui non sei iscritto.",
    onShow: function(){$('#sub_nodes + li a').click();},
    backdrop: false,
    placement: "right"
});

tour.addStep({
    element: "#node_search", 
    title: "Cerca Argomenti", 
    content: "Naturalmente puoi cercare altri <strong>argomenti di tuo interesse</strong>: Scuole, Città, Zone, oppure argomenti di particolare interesse.", 
    backdrop: false,
    placement: "right"
});

tour.addStep({
    element: "#main_stream", 
    title: "Messaggi", 
    content: "Qui vengono <strong>mostrati i messaggi</strong>.", 
    onShow: function(){$('#main_stream_list li:first-child .s_post_title_1').click();},
    backdrop: false,
    placement: "top"
});

tour.addStep({
    element: "#node_subscription", 
    title: "Messaggi", 
    content: "Qui <strong>controlli la tua iscrizione a un Argomento</strong>, e se e con che frequenza ricevere notifiche via mail.", 
    backdrop: false,
    placement: "bottom"
});

tour.addStep({
    element: "#add_new", 
    title: "Messaggi", 
    content: "Con questo pulsante puoi <strong>pubblicare messaggi su un Argomento</strong>.", 
    backdrop: false,
    placement: "right"
});

tour.addStep({
    element: "#main_stream_list li:first-child .s_post_title", 
    title: "Messaggi", 
    content: "Clicca sul titolo del messaggio per <strong>mostrarne tutto il contenuto</strong>.", 
    backdrop: false,
    placement: "top"
});

tour.addStep({
    element: "#main_stream_list li:first-child .show_comment_form", 
    title: "Messaggi", 
    content: "Clicca qui per <strong>aggiungere un commento</strong>", 
    backdrop: false,
    placement: "bottom"
    
});

tour.addStep({
    element: "#main_stream_list li:first-child .post_reshare", 
    title: "Messaggi", 
    content: "Puoi <strong>'inoltrare' un messaggio su un altro Argomento</strong>, ad esempio da una Scuola alla Città, o viceversa.", 
    backdrop: false,
    placement: "bottom"
    
});

tour.addStep({
    element: "#main_stream_list li:first-child .post_vote", 
    title: "Messaggi", 
    content: "Puoi <strong>esprimere il tuo 'gradimento' al post</strong> o al commento", 
    backdrop: false,
    placement: "bottom"
    
});

tour.addStep({
    element: "#ntf_cnt", 
    title: "Notifiche", 
    content: "<p>Quando pubblichi un messaggio o un commento, le altre persone iscritte al sito ricevono delle <strong>notifiche</strong>.</p><p>Qui vedi il <strong>numero di notifiche che ti riguardano</strong>.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#ntf_cnt", 
    title: "Notifiche", 
    content: "<p>Cliccando sul numero, mostri l'<strong>elenco delle ultime notifiche</strong>, se presenti.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#stream_nav", 
    title: "Attività", 
    content: "<p>Passiamo alle altre aree. Per tornare a questa area, clicca su 'Attività' oppure sul logo in alto a sinistra.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#nodes_nav", 
    title: "Argomenti", 
    content: "<p>Qui puoi <strong>consultare gli Argomenti</strong>, cercanoo nelle liste dei più attivi o recenti.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#menu_nav", 
    title: "Menu", 
    content: "<p>Qui puoi consultare il <strong>menù previsto</strong>, se è stato configurato per la Scuola selezionata</p>", 
    backdrop: false,
    placement: "bottom"    
});


tour.addStep({
    element: "#stats_nav", 
    title: "Statistiche", 
    content: "<p>Qui puoi consultare le statistiche sgli indicatori del livello del servizio di ristorazione, elaborate dai dati inseriti nelle schede di ispezione delle <strong>Commissioni Mensa</strong></p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#commissioni_nav", 
    title: "Commissioni", 
    content: "<p>Qui puoi consultare le <strong>Scuole</strong> sulla mappa della Città selezionata.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#contatti_nav", 
    title: "Contatti", 
    content: "<p>Qui puoi consultare l'<strong>elenco degli altri iscritti</strong> al sito per Scuola</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#search_nav", 
    title: "Ricerca", 
    content: "<p>Puoi <strong>cercare i messaggi</strong> specificando le parole chiave, come in un normale motore di ricerca.</p>", 
    backdrop: false,
    placement: "bottom"    
});

tour.addStep({
    element: "#start_tour",
    title: "Fine", 
    content: "<p><strong>E con questo è tutto</strong>.</p><p>Puoi <strong>riavviare questo 'tour' cliccando sul '?'</strong> qui in alto.</p><p>Ciao!.</p>", 
    backdrop: false,
    placement: "bottom"    
});

function start_tour() {
    tour.showStep(0);
    tour.start(true);
}

function welcome_dialog() {
    $('.start_tour').click(function(){
        $('#welcome_dialog').modal('hide');
        start_tour();
    });
    $('#welcome_dialog').modal('show');
}
