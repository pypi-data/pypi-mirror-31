!function(){"use strict";function e(e,t){function n(s,i,r){var o=new WebSocket(e),a=!1,d=function e(){if(o.removeEventListener("close",e),a)r(u);else if(0!==s){var t=-1===s?-1:s-1;setTimeout(function(){return n(t,i,r)},1e3)}else r(c)};o.addEventListener("message",function e(n){switch(JSON.parse(n.data).type){case"auth_required":"authToken"in t?o.send(JSON.stringify({type:"auth",api_password:t.authToken})):(a=!0,o.close());break;case"auth_invalid":a=!0,o.close();break;case"auth_ok":o.removeEventListener("message",e),o.removeEventListener("close",d),o.removeEventListener("error",d),i(o)}}),o.addEventListener("close",d),o.addEventListener("error",d)}return new Promise(function(e,s){return n(t.setupRetry||0,e,s)})}function t(e){return e.result}function n(t,n){return void 0===n&&(n={}),e(t,n).then(function(e){var s=new a(t,n);return s.setSocket(e),s})}function s(e,t){return e._subscribeConfig?e._subscribeConfig(t):new Promise(function(n,s){var i=null,r=null,o=[],c=null;t&&o.push(t);var u=function(e){i=Object.assign({},i,e);for(var t=0;t<o.length;t++)o[t](i)},a=function(e,t){return u({services:Object.assign({},i.services,(n={},n[e]=t,n))});var n},d=function(){return Promise.all([e.getConfig(),e.getPanels(),e.getServices()]).then(function(e){var t=e[0],n=e[1],s=e[2];u({core:t,panels:n,services:s})})},f=function(e){e&&o.splice(o.indexOf(e),1),0===o.length&&r()};e._subscribeConfig=function(e){return e&&(o.push(e),null!==i&&e(i)),c.then(function(){return function(){return f(e)}})},(c=Promise.all([e.subscribeEvents(function(e){if(null!==i){var t=Object.assign({},i.core,{components:i.core.components.concat(e.data.component)});u({core:t})}},"component_loaded"),e.subscribeEvents(function(e){if(null!==i){var t,n=e.data,s=n.domain,r=n.service,o=Object.assign({},i.services[s]||{},(t={},t[r]={description:"",fields:{}},t));a(s,o)}},"service_registered"),e.subscribeEvents(function(e){if(null!==i){var t=e.data,n=t.domain,s=t.service,r=i.services[n];if(r&&s in r){var o={};Object.keys(r).forEach(function(e){e!==s&&(o[e]=r[e])}),a(n,o)}}},"service_removed"),d()])).then(function(s){var i=s[0],o=s[1],c=s[2];r=function(){removeEventListener("ready",d),i(),o(),c()},e.addEventListener("ready",d),n(function(){return f(t)})},function(){return s()})})}function i(e,t){return e._subscribeEntities?e._subscribeEntities(t):new Promise(function(n,s){function i(){return e.getStates().then(function(e){o=function(e){for(var t,n={},s=0;s<e.length;s++)n[(t=e[s]).entity_id]=t;return n}(e);for(var t=0;t<u.length;t++)u[t](o)})}function r(t){t&&u.splice(u.indexOf(t),1),0===u.length&&(c(),e.removeEventListener("ready",i),e._subscribeEntities=null)}var o=null,c=null,u=[],a=null;t&&u.push(t),e._subscribeEntities=function(e){return e&&(u.push(e),null!==o&&e(o)),a.then(function(){return function(){return r(e)}})},(a=Promise.all([e.subscribeEvents(function(e){if(null!=o){var t=e.data,n=t.entity_id,s=t.new_state;o=s?function(e,t){var n=Object.assign({},e);return n[t.entity_id]=t,n}(o,s):function(e,t){var n=Object.assign({},e);return delete n[t],n}(o,n);for(var i=0;i<u.length;i++)u[i](o)}},"state_changed"),i()])).then(function(s){var o=s[0];c=o,e.addEventListener("ready",i),n(function(){return r(t)})},function(){return s()})})}function r(e){return e.substr(0,e.indexOf("."))}function o(e,t){var n={};return t.attributes.entity_id.forEach(function(t){var s=e[t];s&&(n[s.entity_id]=s)}),n}var c=1,u=2,a=function(e,t){this.url=e,this.options=t||{},this.commandId=1,this.commands={},this.eventListeners={},this.closeRequested=!1,this._handleMessage=this._handleMessage.bind(this),this._handleClose=this._handleClose.bind(this)};a.prototype.setSocket=function(e){var t=this,n=this.socket;if(this.socket=e,e.addEventListener("message",this._handleMessage),e.addEventListener("close",this._handleClose),n){var s=this.commands;this.commandId=1,this.commands={},Object.keys(s).forEach(function(e){var n=s[e];n.eventType&&t.subscribeEvents(n.eventCallback,n.eventType).then(function(e){n.unsubscribe=e})}),this.fireEvent("ready")}},a.prototype.addEventListener=function(e,t){var n=this.eventListeners[e];n||(n=this.eventListeners[e]=[]),n.push(t)},a.prototype.removeEventListener=function(e,t){var n=this.eventListeners[e];if(n){var s=n.indexOf(t);-1!==s&&n.splice(s,1)}},a.prototype.fireEvent=function(e){var t=this;(this.eventListeners[e]||[]).forEach(function(e){return e(t)})},a.prototype.close=function(){this.closeRequested=!0,this.socket.close()},a.prototype.getStates=function(){return this.sendMessagePromise({type:"get_states"}).then(t)},a.prototype.getServices=function(){return this.sendMessagePromise({type:"get_services"}).then(t)},a.prototype.getPanels=function(){return this.sendMessagePromise({type:"get_panels"}).then(t)},a.prototype.getConfig=function(){return this.sendMessagePromise({type:"get_config"}).then(t)},a.prototype.callService=function(e,t,n){return this.sendMessagePromise(function(e,t,n){var s={type:"call_service",domain:e,service:t};return n&&(s.service_data=n),s}(e,t,n))},a.prototype.subscribeEvents=function(e,t){var n=this;return this.sendMessagePromise(function(e){var t={type:"subscribe_events"};return e&&(t.event_type=e),t}(t)).then(function(s){var i={eventCallback:e,eventType:t,unsubscribe:function(){return n.sendMessagePromise(function(e){return{type:"unsubscribe_events",subscription:e}}(s.id)).then(function(){delete n.commands[s.id]})}};return n.commands[s.id]=i,function(){return i.unsubscribe()}})},a.prototype.ping=function(){return this.sendMessagePromise({type:"ping"})},a.prototype.sendMessage=function(e){this.socket.send(JSON.stringify(e))},a.prototype.sendMessagePromise=function(e){var t=this;return new Promise(function(n,s){t.commandId+=1;var i=t.commandId;e.id=i,t.commands[i]={resolve:n,reject:s},t.sendMessage(e)})},a.prototype._handleMessage=function(e){var t=JSON.parse(e.data);switch(t.type){case"event":this.commands[t.id].eventCallback(t.event);break;case"result":t.success?this.commands[t.id].resolve(t):this.commands[t.id].reject(t.error),delete this.commands[t.id]}},a.prototype._handleClose=function(){var t=this;if(Object.keys(this.commands).forEach(function(e){var n=t.commands[e].reject;n&&n(function(e,t){return{type:"result",success:!1,error:{code:e,message:t}}}(3,"Connection lost"))}),!this.closeRequested){this.fireEvent("disconnected");var n=Object.assign({},this.options,{setupRetry:0});!function s(i){setTimeout(function(){e(t.url,n).then(function(e){return t.setSocket(e)},function(){return s(i+1)})},1e3*Math.min(i,5))}(0)}};var d="group.default_view",f=Object.freeze({ERR_CANNOT_CONNECT:c,ERR_INVALID_AUTH:u,createConnection:n,subscribeConfig:s,subscribeEntities:i,getGroupEntities:o,splitByGroups:function(e){var t=[],n={};return Object.keys(e).forEach(function(s){var i=e[s];"group"===r(s)?t.push(i):n[s]=i}),t.forEach(function(e){return e.attributes.entity_id.forEach(function(e){delete n[e]})}),{groups:t,ungrouped:n}},getViewEntities:function(e,t){var n={};return t.attributes.entity_id.forEach(function(t){var s=e[t];if(s&&!s.attributes.hidden&&(n[s.entity_id]=s,"group"===r(s.entity_id))){var i=o(e,s);Object.keys(i).forEach(function(e){var t=i[e];t.attributes.hidden||(n[e]=t)})}}),n},extractViews:function(e){var t=[];return Object.keys(e).forEach(function(n){var s=e[n];s.attributes.view&&t.push(s)}),t.sort(function(e,t){return e.entity_id===d?-1:t.entity_id===d?1:e.attributes.order-t.attributes.order}),t},extractDomain:r,extractObjectId:function(e){return e.substr(e.indexOf(".")+1)}});window.HAWS=f,window.HASS_DEMO=!1,window.HASS_DEV=!1,window.HASS_BUILD="es5",window.HASS_VERSION="20180417.0";var v=window.createHassConnection=function(e){var t=("https:"===window.location.protocol?"wss":"ws")+"://"+window.location.host+"/api/websocket?"+window.HASS_BUILD,r={setupRetry:10};return void 0!==e&&(r.authToken=e),n(t,r).then(function(e){return i(e),s(e),e})};"1"===window.noAuth?window.hassConnection=v():window.localStorage.authToken?window.hassConnection=v(window.localStorage.authToken):window.hassConnection=null,window.addEventListener("error",function(e){var t=document.querySelector("home-assistant");t&&t.hass&&t.hass.callService&&t.hass.callService("system_log","write",{logger:"frontend."+(window.HASS_DEV?"js_dev":"js")+"."+window.HASS_BUILD+"."+window.HASS_VERSION.replace(".",""),message:e.filename+":"+e.lineno+":"+e.colno+" "+e.message})})}();