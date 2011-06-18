<div class="navigation" id="navigation">
<span class="goog-ws-half-width">
<a href="/" class="btn"><b><b><b><b  style="font-weight:bold !important;">Home Page</b></b></b></b></a>
</span>
<span class="goog-ws-half-width">
<a href="/commissione" class="btn"><b><b><b><b  style="font-weight:bold !important;">Commissioni</b></b></b></b></a>
</span>
<span class="goog-ws-half-width">
<a href="/stats" class="btn"><b><b><b><b  style="font-weight:bold !important;">Statistiche</b></b></b></b></a>
</span>
{% if user and commissario %}
<span class="goog-ws-half-width">
<a href="/commissario" class="btn"><b><b><b><b  style="font-weight:bold !important;">Area Commissari</b></b></b></b></a>
</span>
{% endif %}
{% if user and not commissario %}
<span class="goog-ws-half-width">
<a href="/commissario/registrazione" class="btn"><b><b><b><b  style="font-weight:bold !important;">Registrazione Nuovo Commissario</b></b></b></b></a>
</span>
{% endif %}
{% if admin %}
<span class="goog-ws-half-width">
<a href="/admin" class="btn"><b><b><b><b  style="font-weight:bold !important;">Gestione Sistema</b></b></b></b></a>
</span>
{% endif %}
<span class="goog-ws-half-width">
<a href="{{url}}" class="btn"><b><b><b><b  style="font-weight:bold !important;">{{url_linktext}} {{user.nickname}} - {{user.email}}</b></b></b></b></a>
</span>
</div>
