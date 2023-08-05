webpackJsonp([39],{0:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}var i=e(104),o=_interopRequireDefault(i),n=e(5),r=_interopRequireDefault(n),a=e(32),u=_interopRequireDefault(a);e(1006);var l=e(338),d=_interopRequireDefault(l),c=e(342),p=_interopRequireDefault(c);new u.default({mixins:[o.default],components:{ShareButton:d.default,DiscussionThreads:p.default},ready:function(){r.default.debug("Post page ready")}})},114:function(s,t,e){var i,o;i=e(309),o=e(331),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},309:function(s,t){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var e=52;t.default={props:{user:Object,size:{type:Number,default:e}}}},310:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}Object.defineProperty(t,"__esModule",{value:!0});var i=e(115),o=(_interopRequireDefault(i),e(74)),n=_interopRequireDefault(o);t.default={props:{title:{type:String,required:!0},url:{type:String,required:!0}},filters:{encode:encodeURIComponent},methods:{click:function(){n.default.publish("SHARE"),this.$refs.popover.show=!1}}}},311:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}Object.defineProperty(t,"__esModule",{value:!0});var i=e(5),o=_interopRequireDefault(i);t.default={props:{discussionId:String},data:function(){return{sending:!1,comment:""}},methods:{prefill:function(s){s=s||"",this.comment=s,this.$els.textarea.setSelectionRange(s.length,s.length),this.$els.textarea.focus()},submit:function(){var s=this;this.sending=!0,this.$api.post("discussions/"+this.discussionId+"/",{comment:this.comment}).then(function(t){s.$dispatch("discussion:updated",t),s.comment="",s.sending=!1,document.location.href="#discussion-"+s.discussionId+"-"+(t.discussion.length-1)}).catch(function(t){var e=s._("An error occured while submitting your comment");s.$dispatch("notify.error",e),o.default.error(t),s.sending=!1})}}}},312:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}Object.defineProperty(t,"__esModule",{value:!0});var i=e(18),o=_interopRequireDefault(i),n=e(114),r=_interopRequireDefault(n),a=e(339),u=_interopRequireDefault(a),l=e(17),d=_interopRequireDefault(l);t.default={components:{Avatar:r.default,ThreadForm:u.default},props:{discussion:Object,position:Number},data:function(){return{detailed:!1,formDisplayed:!1,currentUser:o.default.user}},events:{"discussion:updated":function(s){return this.hideForm(),!0}},computed:{discussionIdAttr:function(){return"discussion-"+this.discussion.id},createdDate:function(){return(0,d.default)(this.discussion.created).format("LL")},closedDate:function(){return(0,d.default)(this.discussion.closed).format("LL")}},methods:{toggleDiscussions:function(){this.detailed=!this.detailed},displayForm:function(){this.$auth(this._("You need to be logged in to comment.")),this.formDisplayed=!0,this.detailed=!0},hideForm:function(){this.formDisplayed=!1},start:function(s){var t=this;this.displayForm(),this.$nextTick(function(){t.$els.form&&t.$refs.form&&(t.$scrollTo(t.$els.form),t.$refs.form.prefill(s))})},focus:function(s){var t=this;this.detailed=!0,s?this.$nextTick(function(){t.$scrollTo("#"+t.discussionIdAttr+"-"+s)}):this.$scrollTo(this)},formatDate:function(s){return(0,d.default)(s).format("LL")}}}},313:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}Object.defineProperty(t,"__esModule",{value:!0});var i=e(5),o=_interopRequireDefault(i);t.default={props:{subjectId:String,subjectClass:String,position:Number},data:function(){return{sending:!1,title:"",comment:""}},methods:{prefill:function(s,t){t=t||"",this.comment=t,this.title=s||"",s?(this.$els.textarea.setSelectionRange(t.length,t.length),this.$els.textarea.focus()):this.$els.title.focus()},submit:function(){var s=this,t={title:this.title,comment:this.comment,subject:{id:this.subjectId,class:this.subjectClass}};this.sending=!0,this.$api.post("discussions/",t).then(function(t){s.$dispatch("discussion:created",t),s.title="",s.comment="",s.sending=!1,document.location.href="#discussion-"+t.id}).catch(function(t){var e=s._("An error occured while submitting your comment");s.$dispatch("notify:error",e),o.default.error(t),s.sending=!1})}}}},314:function(s,t,e){"use strict";function _interopRequireDefault(s){return s&&s.__esModule?s:{default:s}}Object.defineProperty(t,"__esModule",{value:!0});var i=e(124),o=_interopRequireDefault(i),n=e(18),r=_interopRequireDefault(n),a=e(114),u=_interopRequireDefault(a),l=e(340),d=_interopRequireDefault(l),c=e(341),p=_interopRequireDefault(c),f=e(5),m=_interopRequireDefault(f),h=/^#discussion-([0-9a-f]{24})$/,g=/^#discussion-([0-9a-f]{24})-(\d+)$/,v=/^#discussion-([0-9a-f]{24})-new-comment$/;t.default={components:{Avatar:u.default,DiscussionThread:d.default,ThreadsForm:p.default},data:function(){return{discussions:[],formDisplayed:!1,currentUser:r.default.user}},props:{subjectId:String,subjectClass:String},events:{"discussion:created":function(s){var t=this;this.hideForm(),this.discussions.unshift(s),this.$nextTick(function(){var e=t.threadFor(s.id);e.detailed=!0,t.$scrollTo(e)})},"discussion:updated":function(s){var t=this.discussions.indexOf(this.discussions.find(function(t){return t.id==s.id}));this.discussions.$set(t,s)}},ready:function(){var s=this;this.$api.get("discussions/",{for:this.subjectId}).then(function(t){s.discussions=t.data,document.location.hash&&s.$nextTick(function(){s.jumpToHash(document.location.hash)})}).catch(m.default.error.bind(m.default))},methods:{displayForm:function(){this.$auth(this._("You need to be logged in to start a discussion.")),this.formDisplayed=!0},hideForm:function(){this.formDisplayed=!1},start:function(s,t){var e=this;this.displayForm(),this.$nextTick(function(){e.$els.form&&e.$refs.form&&(e.$scrollTo(e.$els.form),e.$refs.form.prefill(s,t))})},threadFor:function(s){return this.$refs.threads.find(function(t){return t.discussion.id==s})},jumpToHash:function(s){if("#discussion-create"===s)this.start();else if(h.test(s)){var t=s.match(h),e=(0,o.default)(t,2),i=e[1];this.threadFor(i).focus()}else if(g.test(s)){var n=s.match(g),r=(0,o.default)(n,3),a=r[1],u=r[2];this.threadFor(a).focus(u)}else if(v.test(s)){var l=s.match(v),d=(0,o.default)(l,2),c=d[1];this.threadFor(c).start()}}}}},324:function(s,t,e){t=s.exports=e(14)(),t.push([s.id,"","",{version:3,sources:[],names:[],mappings:"",file:"share.vue",sourceRoot:"webpack://"}])},325:function(s,t,e){t=s.exports=e(14)(),t.push([s.id,".discussion-thread .list-group-item p.list-group-item-heading a,.discussion-thread .list-group-item p.list-group-item-heading a:hover{text-decoration:underline}.discussion-thread .list-group-item.list-group-indent{margin-left:54px;height:inherit;min-height:54px}.discussion-thread .list-group-item.body-only{margin-top:-10px}.discussion-thread .list-group-item.body-only .list-group-item-heading{margin:5px}","",{version:3,sources:["/./js/components/discussions/thread.vue"],names:[],mappings:"AAAA,sIAAsI,yBAAyB,CAAC,sDAAsD,iBAAiB,eAAe,eAAe,CAAC,8CAA8C,gBAAgB,CAAC,uEAAuE,UAAU,CAAC",file:"thread.vue",sourcesContent:[".discussion-thread .list-group-item p.list-group-item-heading a,.discussion-thread .list-group-item p.list-group-item-heading a:hover{text-decoration:underline}.discussion-thread .list-group-item.list-group-indent{margin-left:54px;height:inherit;min-height:54px}.discussion-thread .list-group-item.body-only{margin-top:-10px}.discussion-thread .list-group-item.body-only .list-group-item-heading{margin:5px}"],sourceRoot:"webpack://"}])},326:function(s,t,e){t=s.exports=e(14)(),t.push([s.id,".discussion-threads .list-group-form{height:inherit}.discussion-threads .list-group-form form{padding:1em}","",{version:3,sources:["/./js/components/discussions/threads.vue"],names:[],mappings:"AAAA,qCAAqC,cAAc,CAAC,0CAA0C,WAAW,CAAC",file:"threads.vue",sourcesContent:[".discussion-threads .list-group-form{height:inherit}.discussion-threads .list-group-form form{padding:1em}"],sourceRoot:"webpack://"}])},331:function(s,t){s.exports=' <a class=avatar :href=user.url :title="user | display"> <img class=avatar :src="user | avatar_url size" :alt="user | display" :width=size :height=size> </a> '},332:function(s,t){s.exports=' <button type=button class="btn btn-primary btn-share" :title="_(\'Share\')" v-tooltip v-popover popover-large :popover-title="_(\'Share\')"> <span class="fa fa-share-alt"></span> <div class="btn-group btn-group-lg" data-popover-content> <a class="btn btn-link" title=Google+ @click=click href="https://plus.google.com/share?url={{url|encode}}" target=_blank> <span class="fa fa-2x fa-google-plus"></span> </a> <a class="btn btn-link" title=Twitter @click=click href="https://twitter.com/home?status={{title|encode}}%20-%20{{url|encode}}" target=_blank> <span class="fa fa-2x fa-twitter"></span> </a> <a class="btn btn-link" title=Facebook @click=click href="https://www.facebook.com/sharer/sharer.php?u={{url|encode}}" target=_blank> <span class="fa fa-2x fa-facebook"></span> </a> <a class="btn btn-link" title=LinkedIn @click=click href="https://www.linkedin.com/shareArticle?mini=true&url={{url|encode}}&title={{title|encode}}" target=_blank> <span class="fa fa-2x fa-linkedin"></span> </a> </div> </button> '},333:function(s,t){s.exports=' <form role=form class="clearfix animated" @submit.prevent=submit> <div class=form-group> <label for=comment-new-message>{{ _(\'Comment\') }}</label> <textarea v-el:textarea id=comment-new-message v-model=comment class=form-control rows=3 required></textarea> </div> <button type=submit :disabled="this.sending || !this.comment" class="btn btn-primary btn-block pull-right submit-new-message"> {{ _(\'Submit your comment\') }} </button> </form> '},334:function(s,t){s.exports=' <div class=discussion-thread> <div class=list-group-item :id=discussionIdAttr @click=toggleDiscussions :class="{expanded: detailed}"> <div class="format-label pull-left"> <avatar :user=discussion.user></avatar> </div> <span class=list-group-item-link> <a href="#{{ discussionIdAttr }}"><span class="fa fa-link"></span></a> </span> <h4 class="list-group-item-heading ellipsis open-discussion-thread"> <span>{{ discussion.title }}</span> <span v-if=discussion.closed class="fa fa-microphone-slash"></span> </h4> <p class="list-group-item-text ellipsis open-discussion-thread list-group-message-number-{{ discussion.id }}"> <span v-if=!discussion.closed>{{ _(\'Discussion started on {created} with {count} messages.\', {created: createdDate, count: discussion.discussion.length}) }}</span> <span v-if=discussion.closed>{{ _(\'Discussion closed on {closed} with {count} messages.\', {closed: closedDate, count: discussion.discussion.length}) }}</span> </p> </div> <div v-for="(index, response) in discussion.discussion" id="{{ discussionIdAttr }}-{{ index }}" class="list-group-item list-group-indent animated discussion-messages-list" :class="{\'body-only\': index == 0}" v-show=detailed> <template v-if="index > 0"> <div class="format-label pull-left"> <avatar :user=response.posted_by></avatar> </div> <span class=list-group-item-link> <a href="#{{ discussionIdAttr }}-{{ index }}"><span class="fa fa-link"></span></a> </span> <div class="list-group-item-text ellipsis">{{ _(\'Comment posted on {posted_on}\', { posted_on: formatDate(response.posted_on) }) }}</div> </template> <p class=list-group-item-heading> {{{ response.content | markdown }}} </p> </div> <a v-if=!discussion.closed class="list-group-item add new-comment list-group-indent animated" v-show="!formDisplayed && detailed" @click=displayForm> <div class="format-label pull-left">+</div> <h4 class=list-group-item-heading> {{ _(\'Add a comment\') }} </h4> </a> <div v-el:form id="{{ discussionIdAttr }}-new-comment" v-show=formDisplayed v-if=currentUser class="list-group-item list-group-form list-group-indent animated"> <div class="format-label pull-left"> <avatar :user=currentUser></avatar> </div> <span class=list-group-item-link> <a href="#{{ discussionIdAttr }}-new-comment"><span class="fa fa-link"></span></a> <a @click=hideForm><span class="fa fa-times"></span></a> </span> <h4 class=list-group-item-heading> {{ _(\'Commenting on this thread\') }} </h4> <p class=list-group-item-text> {{ _("You\'re about to answer to this particular thread about:") }}<br/> {{ discussion.title }} </p> <thread-form v-ref:form :discussion-id=discussion.id></thread-form> </div> </div> '},335:function(s,t){s.exports=" <form role=form class=\"clearfix animated\" @submit.prevent=submit> <div class=form-group> <label for=title-new-discussion>{{ _('Title') }}</label> <input v-el:title type=text id=title-new-discussion v-model=title class=form-control required/> <label for=comment-new-discussion>{{ _('Comment') }}</label> <textarea v-el:textarea id=comment-new-discussion v-model=comment class=form-control rows=3 required></textarea> </div> <button type=submit :disabled=\"this.sending || !this.title || !this.comment\" class=\"btn btn-primary btn-block pull-right submit-new-discussion\"> {{ _('Start a discussion') }} </button> </form> "},336:function(s,t){s.exports=' <div class="list-group resources-list smaller discussion-threads"> <discussion-thread v-ref:threads v-for="discussion in discussions" :discussion=discussion track-by=id> </discussion-thread> <a class="list-group-item add new-discussion" @click=displayForm v-show=!formDisplayed> <div class="format-label pull-left">+</div> <h4 class=list-group-item-heading>{{ _(\'Start a new discussion\') }}</h4> </a> <div v-el:form id=discussion-create v-show=formDisplayed v-if=currentUser class="list-group-item list-group-form list-group-form-discussion animated"> <div class="format-label pull-left"> <avatar :user=currentUser></avatar> </div> <span class=list-group-item-link> <a href=#discussion-create><span class="fa fa-link"></span></a> <a @click=hideForm><span class="fa fa-times"></span></a> </span> <h4 class=list-group-item-heading> {{ _(\'Starting a new discussion thread\') }} </h4> <p class=list-group-item-text> {{ _("You\'re about to start a new discussion thread. Make sure that a thread about the same topic doesn\'t exist yet just above.") }} </p> <threads-form v-ref:form :subject-id=subjectId :subject-class=subjectClass></threads-form> </div> </div> '},338:function(s,t,e){var i,o;e(344),i=e(310),o=e(332),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},339:function(s,t,e){var i,o;i=e(311),o=e(333),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},340:function(s,t,e){var i,o;e(345),i=e(312),o=e(334),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},341:function(s,t,e){var i,o;i=e(313),o=e(335),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},342:function(s,t,e){var i,o;e(346),i=e(314),o=e(336),s.exports=i||{},s.exports.__esModule&&(s.exports=s.exports.default),o&&(("function"==typeof s.exports?s.exports.options||(s.exports.options={}):s.exports).template=o)},344:function(s,t,e){var i=e(324);"string"==typeof i&&(i=[[s.id,i,""]]);e(15)(i,{sourceMap:!0});i.locals&&(s.exports=i.locals)},345:function(s,t,e){var i=e(325);"string"==typeof i&&(i=[[s.id,i,""]]);e(15)(i,{sourceMap:!0});i.locals&&(s.exports=i.locals)},346:function(s,t,e){var i=e(326);"string"==typeof i&&(i=[[s.id,i,""]]);e(15)(i,{sourceMap:!0});i.locals&&(s.exports=i.locals)},1006:1007});
//# sourceMappingURL=post.js.map