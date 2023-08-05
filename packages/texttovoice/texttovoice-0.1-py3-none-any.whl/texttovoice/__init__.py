#!/usr/bin/python

import cgi
import cgitb
#cgitb.enable()
cgitb.enable(display=1, logdir="/Users/Mihai/ml/logs/logs.txt")


class Page: 
     def __init__(self, title):
         self.title=title
	    # Header tells the browser how to render the HTML.
         print ("Content-Type: text/html\n\n")

	# Define function to generate HTML form.
     def generate_form(self):

         print ("<HTML>\n")
         print ("<HEAD>\n")
         print ("\t<TITLE>" + self.title + "</TITLE>\n")
         print ("</HEAD>\n")
         print ("<BODY BGCOLOR = white>\n")
         print ("\t<H3>Please, enter your text.</H3>\n")
         print ("\t<TABLE BORDER = 0>\n")
         print ("\t\t<FORM METHOD = post ACTION = \"cgi_example1.cgi\">\n")
         print ("\t\t<TR><TH>Name:</TH><TD><INPUT type = text \ name = \"name\"></TD><TR>\n")
         print ("\t\t<TR><TH>Age:</TH><TD><INPUT type = text name = \"age\"></TD></TR>\n")
         print ("\t</TABLE>\n")
         print ("\t<INPUT TYPE = hidden NAME = \"action\" VALUE = \"display\">\n")
         print ("\t<INPUT TYPE = submit VALUE = \"Enter\">\n")
         print ("\t</FORM>\n")
         print ("</BODY>\n")
         print ("</HTML>\n")
     
     def display_data (self, name, age):
         print ("<HTML>\n")
         print ("<HEAD>\n")
         print ("\t<TITLE>"+self.title+"</TITLE>\n")
         print ("</HEAD>\n")
         print ("<BODY BGCOLOR = white>\n")
         print (name, ", you are", age, "years old.")
         print ("</BODY>\n")
         print ("</HTML>\n")



def main():
     page = Page('Text to voice assistant')
     form = cgi.FieldStorage()
     if (form.has_key("action") and form.has_key("name") and form.has_key("age")):
         if (form["action"].value == "display"):
            page.display_data(form["name"].value, form["age"].value)
     else:
         page.generate_form()

main()
