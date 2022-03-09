from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import requests


#https://www.youtube.com/watch?v=_8xXrFWcWao
#https://docs.python.org/3/library/xmlrpc.server.html 
#host and port
host = 'localhost'
port = 1234

#server request handler
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
#creating server
server = SimpleXMLRPCServer((host,port), requestHandler=RequestHandler,logRequests=True ,allow_none=True,encoding='utf-8')

#topic class for new topics
class Topic: 
    name = ""
    href = ""
    note = ""
    text = ""
    timestamp = ""
    link = ""


##funtions that can be run 
class FunctionsClass:

    #adding user topics to xml
    def server_get_inputs(self, args):
        
        #get values
        user_topic = args[0] 
        user_note = args[1] 
        user_text = args[2]
        user_date = args[3] 
        user_link = args[4]

        
        #open file 
        tree = ET.parse('xml_db.xml')
        root = tree.getroot()
        
        #topic does not exist
        topic_check = True 
        
        #search file for topic name
        for topic in root.findall('./topic'):

            #found the topic name
            if(topic.attrib['name'] == user_topic):
                topic_check = False

        #adding to xml was success 
        success = False
        
        #https://www.geeksforgeeks.org/modify-xml-files-with-python/ 
        #if has not a topic add to it
        if(topic_check):

            #creating new topic element and giving it name and adding it to root
            newTopic = ET.Element('topic')
            newTopic.attrib['name'] = user_topic
            root.append(newTopic)

            #creating new note to previous newtopic subelement and giving it name value
            note = ET.SubElement(newTopic, "note")
            note.attrib['name'] = user_note

            #creating a new sublements for the note and adding their texts
            note_text = ET.SubElement(note, "text")
            note_text.text = user_text
            note_timestamp = ET.SubElement(note, "timestamp")
            note_timestamp.text = user_date
            note_link = ET.SubElement(note, "link")
            note_link.text = user_link

            #writing the xml 
            tree.write('xml_db.xml')

            #returing that was successful
            success = True
            return success
            

        #does have a topic
        else:

            #find the topic to be added 
            for topic in root.findall('./topic'):
                
                #found the topic naem
                if(topic.attrib['name'] == user_topic):
                    
                    #creating new note to previous topic element and giving it name value
                    newnote = ET.SubElement(topic, 'note')
                    newnote.attrib['name'] = user_note
                    
                    #creating a new sublements for the note and adding their texts
                    note_text = ET.SubElement(newnote, "text")
                    note_text.text = user_text
                    note_timestamp = ET.SubElement(newnote, "timestamp")
                    note_timestamp.text = user_date
                    note_link = ET.SubElement(newnote, "link")
                    note_link.text = user_link

                    #writing the xml 
                    tree.write('xml_db.xml')

                    #returing that was successful
                    success = True
                    return success

        #if something when wrong
        return success

    #getting the contents of the xml topic
    def get_contents(self, arg):

        #wanted topic
        user_topic = arg

        #open file 
        tree = ET.parse('xml_db.xml')
        root = tree.getroot()

        #list that xml values are added to
        query_list = []

        #search for the topics
        for topic in root.iter('topic'):
           
            #found the topic
            if (topic.attrib['name'] == user_topic):

                #if has a link to wikipedia page
                try:
                    href= topic.attrib['href']
                    print(topic.attrib['href'])
                except KeyError:
                    href = "NO LINK"
                
                #go through all of the topic notes
                for note in topic.iter('note'):
                    
                    #creating a new topic object and adding values to it
                    topic = Topic()
                    topic.name = user_topic
                    topic.href = href
                    topic.note = note.attrib['name']
                    topic.text = note.find('text').text
                    
                    topic.timestamp = note.find('timestamp').text
                    try:
                        topic.link = note.find('link').text
                    except:
                        topic.link = "NO LINK"

                    #adding new topic object to list
                    query_list.append(topic)
                
                #breaking the loop as topic was found
                break

        #returning the list to client
        return query_list


    #adding wikipedia link to topic
    def add_wikipedia_topic(self,topic_list):

        #getting the values from the topic list
        topic_name = topic_list[0]
        topic_link = topic_list[1]

        #open file 
        tree = ET.parse('xml_db.xml')
        root = tree.getroot()

        #search file for topic name
        topic_check = False
        for topic in root.findall('./topic'):

            #found the topic
            if(topic.attrib['name'] == topic_name):
                topic_check = True


        #if does not have an existing topic-->return false
        if topic_check == False:
            return False

        #has a topic--> add link to topic 
        else:
            #search for the topics
            for topic in root.iter('topic'):
                #found the topic name
                if (topic.attrib['name'] == topic_name):

                    #adding new link to it and write the file
                    topic.attrib['href'] = topic_link
                    tree.write('xml_db.xml')

                    #was successful
                    return True

        #something when wrong
        return False

#getting data from wikipedia
def get_wikipedia_data(term,limit):

    #https://www.mediawiki.org/wiki/API:Search
    #creaiting new request
    session = requests.Session()

    #url
    url = "https://en.wikipedia.org/w/api.php"

    #open search parameters
    params = {
    "action": "opensearch",
    "namespace": "0",
    "search": term,
    "limit": limit,
    "format": "json"
    }

    #trying to make the request to wikipedia API
    try:
        #making the get request to API
        response = session.get(url=url, params=params)
        
        #returning the data to client
        return response.json()
    #something went wrong
    except:
        return [term,[],[],[]]


#registering created functions to server instance
server.register_instance(FunctionsClass())
server.register_function(get_wikipedia_data)


#starting the server
def main():
    try:
        print('Starting server')
        server.serve_forever() #runnin the server
    except KeyboardInterrupt:
        print('Shutting down the server')
main()