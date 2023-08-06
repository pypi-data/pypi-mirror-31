(window.webpackJsonp=window.webpackJsonp||[]).push([[13],{394:function(e,t,s){"use strict";s.r(t);var i=s(0),a=s(1);s(10);class r extends(window.hassMixins.NavigateMixin(window.hassMixins.EventsMixin(a.a))){static get template(){return i["a"]`
    <style>
      iframe {
        border: 0;
        width: 100%;
        height: 100%;
        display: block;
      }
    </style>
    <iframe
      id='iframe'
      src="[[iframeUrl]]"
    ></iframe>
    `}static get is(){return"ha-panel-hassio"}static get properties(){return{hass:Object,narrow:Boolean,showMenu:Boolean,route:Object,iframeUrl:{type:String,value:window.HASS_DEV?"/home-assistant-polymer/hassio/index.html":"/api/hassio/app-es5/index.html"}}}static get observers(){return["_dataChanged(hass, narrow, showMenu, route)"]}ready(){super.ready(),window.hassioPanel=this}_dataChanged(e,t,s,i){this._updateProperties({hass:e,narrow:t,showMenu:s,route:i})}_updateProperties(e){const t=this.$.iframe.contentWindow&&this.$.iframe.contentWindow.setProperties;if(!t){const t=!this._dataToSet;return this._dataToSet=e,void(t&&setTimeout(()=>{const e=this._dataToSet;this._dataToSet=null,this._updateProperties(e)},100))}t(e)}}customElements.define(r.is,r)}}]);