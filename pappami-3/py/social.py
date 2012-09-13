from py.base import *
from google.appengine.api import users
import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import feedparser
from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from datetime import date, datetime, time, timedelta
from gviz_api import *
from py.model import *
from form import *
from base import BasePage, CMCommissioniDataHandler, user_required, config, handle_404, handle_500
import random
def fix_padding(string):
    lens = len(string)
    lenx = lens - (lens % 4 if lens % 4 else 4)
    try:
        result =string[:lenx]
        return result
    except: 
        pass
    
def get_current_sub(current_user,node):
    if current_user:
        current_user=current_user.key
        current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
        if current_sub is None:
              current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
              memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
       
        return current_sub
    
class NodeHandler(BasePage):
  
  def post(self):
        self.response.out.write("");
        
  def get(self,node_id):
    
   
    node_i=model.Key(urlsafe=node_id).get()
    node=node_i.key
       #if node does not exist
    if not node_i or node_i.active==False :
       
        self.response.clear() 
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il nodo a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return
    
    
   
        
    current_user=self.get_current_user()
    if current_user is None:
        logged=False
        is_sub=False
    else:
        logged=True
        is_sub= node.get().is_user_subscribed(current_user)
     
    #check permission
    can_post=False
    current_user=self.get_current_user()
    current_sub=get_current_sub(current_user,node)
                
    if node_i.is_public:
        template_values = {
          'content': 'social/node.html',
          "user":current_user,
          "node":node_i,
          "is_sub":is_sub,
          "show_sub_button": True if not logged or not is_sub else False,
          "subscriptions": [Commissario.get_by_user(x) for x in node.get().subscription_list()],
          "citta": Citta.get_all(),
          "subscription":current_sub
          }
    else:
        pass
      
    self.getBase(template_values)
    

       
    
    
class SocialTest(BasePage):
  def get(self):
      newsletter=SocialNewsLetter()
      test=newsletter.create_newsletter()
      template_values = {
      'content': 'social/test.html',
      'testa': test
      }
        
      self.getBase(template_values)
    
     
class NodeListHandler(BasePage):
  def get(self):
    geo = model.GeoPt(41.754922,12.502441)
    template_values = {
      'content': 'social/nodelist.html',
      'nodelist': SocialNode.active_nodes(),
      'citta': Citta.get_all(),
      'geo':geo}
        
    self.getBase(template_values)
    
    
       
class SocialPostHandler(BasePage):
    def get(self,id):
        
        op=model.Key(urlsafe=id).get()
                            
        if op is None or type(op) is not SocialPost:
            self.response.clear() 
            self.response.set_status(404)
            template = jinja_environment.get_template('404_custom.html')
            c={"error": "Il post a cui stai provando ad accedere non esiste"}
            t = template.render(c)
            self.response.out.write(t)
            return
        node=op.key.parent()
        op.commissario=Commissario.get_by_user(op.author.get())
        replies=[]
        for x in op.get_discussion():
            
            x.commissario=Commissario.get_by_user(x.author.get())
            replies.append(x)
        
        
        current_user=self.get_current_user()
        current_sub=None
        if current_user is not None:
            current_user=current_user.key
            current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
            if current_sub is None:
                current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
                memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
         
        template_values = {
                           'content': 'social/post.html',
                           'replies': replies,
                           'post': op,
                           'node':node.get(),
                           'user':current_user
                           
                                              }                    
        if current_user:
            template_values['subscription']=current_sub
            template_values["user"]=current_user
        
        self.getBase(template_values)

class SocialMapHandler(webapp.RequestHandler):
      
  def get(self): 
    cursor = self.request.get("cur")

    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))    

    if self.request.get("cmd") == "all":
      markers = memcache.get("markers_social_all"+str(offset))
      if(markers == None):
          
        nodes = SocialNode.get_all_cursor(cursor)
          
        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in nodes :
            i += 1
            if i >= limit:
              break
            if c.geo:
              mark = '<marker key="' + str(c.key.id()) + '" name="' + c.name + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon)
              mark += '" />\n'              
              markers_list.append(mark)
        except:
          logging.error("Timeout")
        if i >= limit:
          markers = "<markers cur='" + nodes.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"
          
        markers = markers + "".join(markers_list) + "</markers>"
        
        memcache.add("markers_all"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)      
    else:
      markers = memcache.get("markers_social"+str(offset))
      if(markers == None):
          
        nodes = SocialNode.get_active_cursor(cursor)

        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in commissioni :
            i += 1
            if i >= limit:
              break
            if c.geo :
                mark = '<marker key="' + str(c.key.id()) + '" name="' + c.name + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon)
                mark += '" />\n'              
                markers_list.append(mark)
        except:
          raise
          logging.error("Timeout")
          
        #logging.info(markers_list)
        if i >= limit:
          markers = "<markers cur='" + nodes.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"
          
        markers = markers + "".join(markers_list) + "</markers>"
        memcache.add("markers_social"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)
     
class SocialSubscribeHandler(webapp.RequestHandler):
       def get(self):
           
          cmd = self.request.get('cmd')
          if cmd == "subscribe":
                 user = model.Key("User", int(self.request.get('user'))).get()
                 node = model.Key("SocialNode", int(self.request.get('node'))).get()
                 node.subscribe_user(user)
                 self.response.headers["Content-Type"] = "text/xml"
                 self.response.out.write("<response>success</response>")
        
          if cmd == "unsubscribe":
                 user = model.Key("User", int(self.request.get('user'))).get()
                 node = model.Key("SocialNode", int(self.request.get('node'))).get()
             
                 node.unsubscribe_user(user)
                 self.response.headers["Content-Type"] = "text/xml"
                 self.response.out.write("<response>success</response>")
             
class SocialManagePost(SocialAjaxHandler):
   def post(self):
       
      
       user=self.request.user
       node=model.Key(urlsafe=self.request.get('node'))
       cmd = self.request.get('cmd')

       if cmd == "create_open_post":
           self.response.headers["Content-Type"] = "text/xml"
           node=node.get()
           if not node.get_subscription(user).can_post:
               self.response.out.write("<response>error</response>")
               return
           post=node.create_open_post(feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),feedparser._sanitizeHTML(self.request.get("title"),"UTF-8"),user)
           self.success("/social/post/"+post.urlsafe())
           
           
       if cmd == "create_reply_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           if post:
            
               node=node.get()
               if not node.get_subscription(user).can_reply:
                   self.success()
                   return
           
               
           post.create_reply_comment(feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),user)  
           
           self.success()
           
           
       if cmd == "delete_reply_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key(urlsafe=self.request.get('post')).get()
               memcache.add("SocialPost-"+str(self.request.get('post')),post)
               
           node=node.get()
           if not node.get_subscription(user).can_admin:
               self.response.out.write("<response>error</response>")
               return
           post.delete_reply_comment(self.request.get('reply'))
           self.response.headers["Content-Type"] = "text/xml"
           self.success()

       if cmd == "delete_open_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           
           if post is None:
              post=model.Key(urlsafe=self.request.get('post')).get()
              
           node=node.get()
           #check admin permissions
           if not node.get_subscription(user).can_admin:
               return    
           #delete replies
           model.delete_multi(model.put_multi(SocialComment.query(ancestor=post.key)))
           post.key.delete()
           memcache.delete("SocialPost-"+str(self.request.get('post')))
           
           
           self.success("/social/node/"+node.key.urlsafe())
       if cmd== "reshare_open_post":
           
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key(urlsafe=self.request.get('post')).get()
               memcache.add("SocialPost-"+str(self.request.get('post')),post)
               
           title=self.request.get('title')
           content=self.request.get('content')
           
           post=post.reshare(node,user,feedparser._sanitizeHTML(content,"UTF-8"),feedparser._sanitizeHTML(title,"UTF-8"))
           self.success("/social/post/"+post.urlsafe())
        
       if cmd == "edit_open_post":

          logging.info(self.request.get('content'))
          post=model.Key(urlsafe=self.request.get('post')).get()
          post.content=feedparser._sanitizeHTML(self.request.get("content"),"UTF-8")
          post=post.put()
          
          memcache.add("SocialPost-"+str(self.request.get('post')),post.get())
          
          if post:
              response = {'response':'success','content':post.get().content}
              json = simplejson.dumps(response)
              self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
              self.response.out.write(json)
             
          
               
       if cmd == "edit_reply_post":
           pass
       if cmd == "content_edit":
           template_values = {
                           'template': 'social/contentedit.html',
                           'post':  self.request.get('post'),
                           'node': self.request.get('node'),
                           'user': self.request.get('user'),
                           'content': self.request.get('content'),
                           
                                              }                    
        
           template = jinja_environment.get_template(template_values["template"])
   
           self.response.write(template.render(template_values))


       
class SocialCreateNodeHandler(BasePage):
    @user_required
    def get(self):  
        template_values = {
                        'content': 'social/createnode.html',
                        "citta" : Citta.get_all(),
                        
        }
        self.getBase(template_values)
        
    def post(self):
        
        node=SocialNode()
        node.name=feedparser._sanitizeHTML(self.request.get("name"),"UTF-8")
        node.description=feedparser._sanitizeHTML(self.request.get("description"),"UTF-8")
        node.default_reply=bool(self.request.get("default_reply"))
        node.default_post=bool(self.request.get("default_post"))
        node.default_admin=bool(self.request.get("default_admin"))
        node.founder=self.get_current_user().key
        logging.info(self.request.get("citta"))
        #node.resource=model.Key(urlsafe=self.request.get("citta")).get().create_resource().key
   
        
        node.put()
        
        self.redirect("/social/node/"+str(node.key.urlsafe()))


class SocialEditNodeHandler(BasePage):
        def get(self,id):  
            node=model.Key(urlsafe=id).get()
            if node is None or type(node) is not SocialNode:
                self.response.clear() 
                self.response.set_status(404)
                template = jinja_environment.get_template('404_custom.html')
                c={"error": "Il post a cui stai provando ad accedere non esiste"}
                t = template.render(c)
                self.response.out.write(t)
                return
            
            template_values = {
                            "content": 'social/editnode.html',
                            "node":node,
                            "citta" : Citta.get_all(),
                            
                            }
            
            
            
            self.getBase(template_values)
        def post(self,id):
            logging.info(self.request.get("node_id"))
            node=model.Key(urlsafe=self.request.get("node_id")).get()
            node.name=feedparser._sanitizeHTML(self.request.get("name"),"UTF-8")
            node.description=feedparser._sanitizeHTML(self.request.get("description"),"UTF-8")
            node.default_reply=bool(self.request.get("default_reply"))
            node.default_post=bool(self.request.get("default_post"))
            node.default_admin=bool(self.request.get("default_admin"))
            node.founder=self.get_current_user().key
            node.put()
            
            self.redirect("/social/node/"+str(node.key.id()))

class SocialPaginationHandler(SocialAjaxHandler):
        def post(self):
                cmd=self.request.get("cmd")
                user=self.request.user
                cursor=self.request.get("cursor")
                if cmd=="node":
                    if not cursor or cursor == "undefined":
                        nodelist, next_curs, more = SocialNode.query().order(-SocialNode.latest_post_date).fetch_page(10) 
                    else:
                         nodelist, next_curs, more = SocialNode.query().order(-SocialNode.latest_post_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                    template_values = {
                            "nodelist":nodelist,
                             }
                    if not nodelist or not next_curs:
                        
                        response = {'response':'no_nodes'}
                        json = simplejson.dumps(response)
                        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                        self.response.out.write(json)
                        return
                        
                    template = jinja_environment.get_template("social/pagination/node.html")
                    
                    html=template.render(template_values)
                    response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                    json = simplejson.dumps(response)
                    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                    self.response.out.write(json)
                 
                if cmd=="post":
                        node=model.Key(urlsafe=self.request.get("node"))
                        if not cursor or cursor == "undefined":
                            postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10) 
                        else:
                             postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                        
                        for x in postlist: 
    
                            x.commissario=Commissario.get_by_user(x.author.get())
                            
                            
                        template_values = {
                                "postlist":postlist,
                                 "cmsro":self.getCommissario(user), 
                                 "subscription": get_current_sub(user,node),
                                 "user": user,
                                 "node":node.get()
                                }
                        if not postlist or not next_curs:
                            
                            response = {'response':'no_posts'}
                            json = simplejson.dumps(response)
                            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                            self.response.out.write(json)
                            return
                            
                                
                        template = jinja_environment.get_template("social/pagination/post.html")
       
                        html=template.render(template_values)
                        response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                        json = simplejson.dumps(response)
                        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                        self.response.out.write(json)
                  
                if cmd=="post_main":
                        node=model.Key(urlsafe=self.request.get("node"))
                        if not cursor or cursor == "undefined":
                            postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10) 
                        else:
                             postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                        
                        for x in postlist: 
    
                            x.commissario=Commissario.get_by_user(x.author.get())
                            
                            
                        template_values = {
                                "postlist":postlist,
                                 "cmsro":self.getCommissario(user), 
                                 "subscription": get_current_sub(user,node),
                                 "user": user,
                                 "node":node.get()
                                }
                        if not postlist or not next_curs:
                            
                            response = {'response':'no_posts'}
                            json = simplejson.dumps(response)
                            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                            self.response.out.write(json)
                            return
                            
                                
                        template = jinja_environment.get_template("social/pagination/post.html")
       
                        html=template.render(template_values)
                        response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                        json = simplejson.dumps(response)
                        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
                        self.response.out.write(json)
        
class SocialMainHandler(BasePage):
    @user_required
    def get(self):
        user=self.get_current_user()
        node_list=SocialNodeSubscription.get_nodes_by_user(user,-SocialNodeSubscription.starting_date)
        
        template_values = {
                        'content': 'social/main_social.html',
                        'node_list':node_list
                        
        }
        self.getBase(template_values)
        
class SocialDLoadHandler(SocialAjaxHandler):
    @user_required
    def post(self):
        cmd=self.request.get("cmd")
        user=self.request.user
        
        if cmd=="modal_reshare":
            template_values = {
                                    "my_nodelist":SocialNodeSubscription.get_nodes_by_user(user) ,
                                    "post":self.request.get("post")
        
                                    }
            
            
            
            template = jinja_environment.get_template("social/ajax/modal_reshare.html")
            html=template.render(template_values)
            response = {'response':'success','html':html}
            json = simplejson.dumps(response)
            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
            self.response.out.write(json)
        

class SocialNewsLetter():
    
      def create_newsletter(self):
          user_list=Commissario.get_all()
          nodes=SocialNode.query().fetch()
          posts_by_node={}
          newsletter_size=10
          titolo="Newsletter Pappa-mi"
          #build a 
          for node in nodes:
              posts=SocialPost.query(ancestor=node.key).order(-SocialPost.creation_date).filter(SocialPost.creation_date>=(datetime.now()-timedelta(weeks=1))).fetch(newsletter_size/2)
              if posts:
                  posts_by_node[''+str(node.key.id())]=posts
          
          for user in user_list:
            
                all_posts=[]
                final_posts=[]
                my_nodes=SocialNodeSubscription.get_nodes_by_user(user.usera.get())
                for node in my_nodes:
                    if posts_by_node.has_key(''+str(node.key.id())):
                    
                       all_posts= all_posts+posts_by_node[''+str(node.key.id())]
                if len(all_posts)<=newsletter_size/2:
                    return
                
                       
                for i in range(newsletter_size):
                    rand=random.randint(0,len(all_posts)-1)
                    final_posts.append(all_posts[rand])
                    
                    
                template = jinja_environment.get_template("social/newsletter.html")
                html=template.render({"posts":final_posts})
                mail.send_mail(sender="Example.com Support <example@pappa-mi.it>",
                to=user.usera.get().email,
                subject=titolo,
                body="",
                html=html
                )
  
app = webapp.WSGIApplication([
    ('/social/node/(.*)', NodeHandler),
    ('/social/nodelist/', NodeListHandler),
    ('/social/post/(.*)', SocialPostHandler),
    ('/social/managepost',SocialManagePost),
    ('/social/test', SocialTest),
    ('/social/socialmap',SocialMapHandler),
    ('/social/subscribe', SocialSubscribeHandler),
    ('/social/createnode', SocialCreateNodeHandler),
    ('/social/editnode/(.*)', SocialEditNodeHandler),
    ('/social/paginate', SocialPaginationHandler),
    ('/social/main', SocialMainHandler),
    ('/social/dload', SocialDLoadHandler),
    ],
                             
    debug = True, config=config)



def main():
  app.run();

if __name__ == "__main__":
  main()
