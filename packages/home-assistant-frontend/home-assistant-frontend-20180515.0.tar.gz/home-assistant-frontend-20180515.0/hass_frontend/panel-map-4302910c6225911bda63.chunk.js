(window.webpackJsonp=window.webpackJsonp||[]).push([[7],{385:function(t,e,i){"use strict";i.r(e);i(78),i(37);var a=i(0),s=i(1);i(135),i(10),i(160);class n extends(window.hassMixins.EventsMixin(s.a)){static get template(){return a["a"]`
    <style is="custom-style" include="iron-positioning"></style>
    <style>
    .marker {
      vertical-align: top;
      position: relative;
      display: block;
      margin: 0 auto;
      width: 2.5em;
      text-align: center;
      height: 2.5em;
      line-height: 2.5em;
      font-size: 1.5em;
      border-radius: 50%;
      border: 0.1em solid var(--ha-marker-color, var(--default-primary-color));
      color: rgb(76, 76, 76);
      background-color: white;
    }
    iron-image {
      border-radius: 50%;
    }
    </style>

    <div class="marker">
      <template is="dom-if" if="[[entityName]]">[[entityName]]</template>
      <template is="dom-if" if="[[entityPicture]]">
        <iron-image sizing="cover" class="fit" src="[[entityPicture]]"></iron-image>
      </template>
    </div>
`}static get is(){return"ha-entity-marker"}static get properties(){return{hass:{type:Object},entityId:{type:String,value:""},entityName:{type:String,value:null},entityPicture:{type:String,value:null}}}ready(){super.ready(),this.addEventListener("click",t=>this.badgeTap(t))}badgeTap(t){t.stopPropagation(),this.entityId&&this.fire("hass-more-info",{entityId:this.entityId})}}customElements.define(n.is,n),window.L.Icon.Default.imagePath="/static/images/leaflet";class r extends(window.hassMixins.LocalizeMixin(s.a)){static get template(){return a["a"]`
    <style include="ha-style">
      #map {
        height: calc(100% - 64px);
        width: 100%;
        z-index: 0;
      }
    </style>

    <app-toolbar>
      <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
      <div main-title>[[localize('panel.map')]]</div>
    </app-toolbar>

    <div id='map'></div>
    `}static get is(){return"ha-panel-map"}static get properties(){return{hass:{type:Object,observer:"drawEntities"},narrow:{type:Boolean},showMenu:{type:Boolean,value:!1}}}connectedCallback(){super.connectedCallback();var t=this._map=window.L.map(this.$.map),e=document.createElement("link");e.setAttribute("href",window.HASS_DEV?"/home-assistant-polymer/bower_components/leaflet/dist/leaflet.css":"/static/images/leaflet/leaflet.css"),e.setAttribute("rel","stylesheet"),this.$.map.parentNode.appendChild(e),t.setView([51.505,-.09],13),window.L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>',maxZoom:18}).addTo(t),this.drawEntities(this.hass),setTimeout(()=>{t.invalidateSize(),this.fitMap()},1)}fitMap(){var t;0===this._mapItems.length?this._map.setView(new window.L.LatLng(this.hass.config.core.latitude,this.hass.config.core.longitude),14):(t=new window.L.latLngBounds(this._mapItems.map(t=>t.getLatLng())),this._map.fitBounds(t.pad(.5)))}drawEntities(t){var e=this._map;if(e){this._mapItems&&this._mapItems.forEach(function(t){t.remove()});var i=this._mapItems=[];Object.keys(t.states).forEach(function(a){var s=t.states[a],n=window.hassUtil.computeStateName(s);if(!(s.attributes.hidden&&"zone"!==window.hassUtil.computeDomain(s)||"home"===s.state)&&"latitude"in s.attributes&&"longitude"in s.attributes){var r;if("zone"===window.hassUtil.computeDomain(s)){if(s.attributes.passive)return;var o="";return o=s.attributes.icon?"<iron-icon icon='"+s.attributes.icon+"'></iron-icon>":n,r=window.L.divIcon({html:o,iconSize:[24,24],className:""}),i.push(window.L.marker([s.attributes.latitude,s.attributes.longitude],{icon:r,interactive:!1,title:n}).addTo(e)),void i.push(window.L.circle([s.attributes.latitude,s.attributes.longitude],{interactive:!1,color:"#FF9800",radius:s.attributes.radius}).addTo(e))}var l=s.attributes.entity_picture||"",c=n.split(" ").map(function(t){return t.substr(0,1)}).join("");r=window.L.divIcon({html:"<ha-entity-marker entity-id='"+s.entity_id+"' entity-name='"+c+"' entity-picture='"+l+"'></ha-entity-marker>",iconSize:[45,45],className:""}),i.push(window.L.marker([s.attributes.latitude,s.attributes.longitude],{icon:r,title:window.hassUtil.computeStateName(s)}).addTo(e)),s.attributes.gps_accuracy&&i.push(window.L.circle([s.attributes.latitude,s.attributes.longitude],{interactive:!1,color:"#0288D1",radius:s.attributes.gps_accuracy}).addTo(e))}})}}}customElements.define(r.is,r)}}]);