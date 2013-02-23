sql2json
========

Small web app for returning sql query results in a json format. 
Takes arbitrary input values and isn't locked to any one sql server.
Queries are stored in mongodb to be reusable. API and interface use Flask underneath.

I developed this to help decrease the number of times I had to write mysql connections and such in my monitoring scripts.. parsing json at a url is so much easier... I also wanted to try writing a web app in python, having never done it before ;)
Hack away, extend it, fix my (probably) messy code, do what you want with it. if you do something cool with it, let me know. 

To get up and running:
+	install mongodb (I developed against 10gen's repo version on Ubuntu found here: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/)
+	install python-mysqldb (I used the Ubuntu Repo version <1.2.3-1build1>)
+	install pymongo (easy_install works fine)
+	install flask (easy_install again)
+	run the app: python ./sql_site.py
+	browse to http://localhost:5000 and try it out

I have a pile of TODO items in this project, and will be continuing development

** Disclaimer **
This application is not meant to be put live on the internet. It has not been hardened beyond disallowing non Select statements and is probably vulnerable to all sorts of attacks. It is meant to be an internal tool, and if your internal resources are attacking your internal apps you have a bigger problem that I can't solve. I provide no warranties of any sort that this software is safe for a public facing server.




