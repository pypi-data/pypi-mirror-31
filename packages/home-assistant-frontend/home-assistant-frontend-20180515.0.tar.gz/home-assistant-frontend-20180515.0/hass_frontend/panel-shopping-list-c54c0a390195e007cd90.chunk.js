(window.webpackJsonp=window.webpackJsonp||[]).push([[6],{172:function(e,t,i){"use strict";i(3),i(18),i(21),i(43);var a=i(4),o=i(0);
/**
@license
Copyright (c) 2015 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
Code distributed by Google as part of the polymer project is also
subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
*/
Object(a.a)({_template:o["a"]`
    <style>
      :host {
        overflow: hidden; /* needed for text-overflow: ellipsis to work on ff */
        @apply --layout-vertical;
        @apply --layout-center-justified;
        @apply --layout-flex;
      }

      :host([two-line]) {
        min-height: var(--paper-item-body-two-line-min-height, 72px);
      }

      :host([three-line]) {
        min-height: var(--paper-item-body-three-line-min-height, 88px);
      }

      :host > ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      :host > ::slotted([secondary]) {
        @apply --paper-font-body1;

        color: var(--paper-item-body-secondary-color, var(--secondary-text-color));

        @apply --paper-item-body-secondary;
      }
    </style>

    <slot></slot>
`,is:"paper-item-body"})},389:function(e,t,i){"use strict";i.r(t);i(136),i(134),i(78),i(150),i(117),i(32),i(42),i(152),i(172),i(53),i(57),i(121);var a=i(0),o=i(1);i(135),i(157),i(10);class p extends(window.hassMixins.LocalizeMixin(o.a)){static get template(){return a["a"]`
    <style include="ha-style">
      :host {
        height: 100%;
      }
      app-toolbar paper-listbox {
        width: 150px;
      }
      app-toolbar paper-item {
        cursor: pointer;
      }
      .content {
        padding-bottom: 32px;
        max-width: 600px;
        margin: 0 auto;
      }
      paper-card {
        display: block;
      }
      paper-icon-item {
        border-top: 1px solid var(--divider-color);
      }
      paper-icon-item:first-child {
        border-top: 0;
      }
      paper-checkbox {
        padding: 11px;
      }
      paper-input {
        --paper-input-container-underline: {
          display: none;
        }
        --paper-input-container-underline-focus: {
          display: none;
        }
        position: relative;
        top: 1px;
      }
      .tip {
        padding: 24px;
        text-align: center;
        color: var(--secondary-text-color);
      }
    </style>

    <app-header-layout has-scrolling-region>
      <app-header slot="header" fixed>
        <app-toolbar>
          <ha-menu-button narrow='[[narrow]]' show-menu='[[showMenu]]'></ha-menu-button>
          <div main-title>[[localize('panel.shopping_list')]]</div>
          <ha-start-voice-button hass='[[hass]]' can-listen='{{canListen}}'></ha-start-voice-button>
          <paper-menu-button
            horizontal-align="right"
            horizontal-offset="-5"
            vertical-offset="-5"
          >
            <paper-icon-button
              icon="mdi:dots-vertical"
              slot="dropdown-trigger"
            ></paper-icon-button>
            <paper-listbox slot="dropdown-content">
              <paper-item
                on-click="_clearCompleted"
              >[[localize('ui.panel.shopping-list.clear_completed')]]</paper-item>
            </paper-listbox>
          </paper-menu-button>
        </app-toolbar>
      </app-header>

      <div class='content'>
        <paper-card>
          <paper-icon-item on-focus='_focusRowInput'>
            <paper-icon-button
              slot="item-icon"
              icon="mdi:plus"
              on-click='_addItem'
            ></paper-icon-button>
            <paper-item-body>
              <paper-input
                id='addBox'
                placeholder="[[localize('ui.panel.shopping-list.add_item')]]"
                on-keydown='_addKeyPress'
                no-label-float
              ></paper-input>
            </paper-item-body>
          </paper-icon-item>

          <template is='dom-repeat' items='[[items]]'>
            <paper-icon-item>
                <paper-checkbox
                  slot="item-icon"
                  checked='{{item.complete}}'
                  on-click='_itemCompleteTapped'
                  tabindex='0'
                ></paper-checkbox>
              <paper-item-body>
                <paper-input
                  id='editBox'
                  no-label-float
                  value='[[item.name]]'
                  on-change='_saveEdit'
                ></paper-input>
              </paper-item-body>
            </paper-icon-item>
          </template>
        </paper-card>
        <div class='tip' hidden$='[[!canListen]]'>
          [[localize('ui.panel.shopping-list.microphone_tip')]]
        </div>
      </div>
    </app-header-layout>
    `}static get is(){return"ha-panel-shopping-list"}static get properties(){return{hass:Object,narrow:Boolean,showMenu:Boolean,canListen:Boolean,items:{type:Array,value:[]}}}connectedCallback(){super.connectedCallback(),this._fetchData=this._fetchData.bind(this),this.hass.connection.subscribeEvents(this._fetchData,"shopping_list_updated").then(function(e){this._unsubEvents=e}.bind(this)),this._fetchData()}disconnectedCallback(){super.disconnectedCallback(),this._unsubEvents&&this._unsubEvents()}_fetchData(){this.hass.callApi("get","shopping_list").then(function(e){e.reverse(),this.items=e}.bind(this))}_itemCompleteTapped(e){e.stopPropagation(),this.hass.callApi("post","shopping_list/item/"+e.model.item.id,{complete:e.target.checked}).catch(()=>this._fetchData())}_addItem(e){this.hass.callApi("post","shopping_list/item",{name:this.$.addBox.value}).catch(()=>this._fetchData()),this.$.addBox.value="",e&&setTimeout(()=>this.$.addBox.focus(),10)}_addKeyPress(e){13===e.keyCode&&this._addItem()}_saveEdit(e){const{index:t,item:i}=e.model,a=e.target.value;a!==i.name&&(this.set(["items",t,"name"],a),this.hass.callApi("post","shopping_list/item/"+i.id,{name:a}).catch(()=>this._fetchData()))}_clearCompleted(){this.hass.callApi("POST","shopping_list/clear_completed")}}customElements.define(p.is,p)}}]);