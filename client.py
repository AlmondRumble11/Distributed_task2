from xmlrpc.client import ServerProxy
from datetime import datetime
import sys

#https://docs.python.org/3/library/xmlrpc.server.html
#server proxy
proxy = ServerProxy('http://localhost:1234')

#showing the data from wikipedia
def show_wikipedia_data(data):

    print("WIKIPEDIA DATA FOR SEARCHTERM: ",data[0])
    print("****************************************")
    
    #how many in the wikipedia results
    counts = []
    count = 1

    #showing the results to user
    for term in data[1]:
        #adding the counts
        counts.append(count)
        print("{}) {}".format(count, term))
        print("Link: {}".format(data[3][count-1]))
        count += 1   
    print("****************************************")

    try:
        #does user want to add the wikipedia link to topic
        want_to_add = input("Do you want to add wikipedia link to existing topic(y/n): ")
        #for topic name and link
        topic_list = []

        #want to add the link
        if(want_to_add == 'y'):

            #need to be num from previous list of data
            while True:
                try:

                    #usr input
                    try:
                        choice = int(input("Give a number from the previous list to be added to that topic: "))
                        #input is from previous data
                        if(choice in counts):
                            
                            #add data to list
                            topic_list.append(data[0])
                            topic_list.append(data[3][choice-1])

                            #return the list
                            return topic_list
                        #not form prev data
                        else:
                            print('Only give number from the previous list of data. Please try again')

                    except KeyboardInterrupt:
                        print('Closing the app')
                        sys.exit(0)

                    
                #not a number
                except ValueError: 
                    print('Only give number from the previous list of data. Please try again')
        
        #not to be added
        else:
            return topic_list
    except KeyboardInterrupt:
        print('Closing the app')
        sys.exit(0)
    
    
 
#getting the user input for a topic
def get_user_input():

    #list for the inputs
    user_input = [0,0,0,0,0]
    
    #inputs
    try:
        topic = input('\nGive a topic name: ')
        note = input('Give a note: ')
        text = input('Give text to topic: ')
        date = datetime.now().strftime('%m/%d/%Y - %H:%M:%S')

            #adding to list
        user_input[0] = topic
        user_input[1] = note
        user_input[2] = text
        user_input[3] = date
        
        #if wants to add link to wikipedia
        wikipedia = input('Do you want to add wikipedia link to note (y/n): ')
        if(wikipedia == 'y'):

            #input
            try:
                wikipedia_term = input('Give a wikipedia searchterm: ')
            except KeyboardInterrupt:
                print('Closing the app')
            #getting wikipedia search result from server
            try:
                wikipedia_data = proxy.get_wikipedia_data(wikipedia_term,1)

                #did not have any data or something went wrong
                if(len(wikipedia_data[3]) == 0):
                        print('No data for that searchterm')
                    
                #had data
                else:
                    print(wikipedia_data[3][0])
                    user_input[4] = wikipedia_data[3][0]
            except ConnectionRefusedError:
                print('Could not connect to wikipedia. Please try again\n')

        else:
            
            user_input[4] = "NO LINK"
            #returning the list

    except KeyboardInterrupt:
        print('Closing the app')
        sys.exit(0)


    return user_input

#menu
def menu():
    while True:
        try:
            print('####################')
            print('1) Write a new topic')
            print('2) Show a topic')
            print('3) Lookup topic from wikipedia')
            print('0) Exit the application')
            print('####################\n')

            #user input
            try:
                choice = int(input('Your choice: '))   
                #need to be correct input
                if((choice == 1) or (choice == 2) or (choice == 3) or (choice == 0)):
                    return choice
                #not correct input
                else: 
                    print('Only 0,1,2,3 can be given. Please try again\n')        
            except KeyboardInterrupt:
                print('Closing the app')
                sys.exit(0)
        #not a number
        except ValueError:
            print('Only 0,1,2,3 can be given. Please try again\n')

            
#showing the topic notes
def show_topic_notes(topic_notes,topic_name):
    print("\n***********************************")
    print("Found {} NOTES for the topic: {}".format(len(topic_notes),topic_name))
    print("Here is WIKIPEDIA LINK to get more info about the topic: ",topic_notes[0]['href'])
    count = 1
    for note in topic_notes:
        print("\n------------------{}----------------".format(count))
        print("Note:",note['note'])
        print("Text:",note['text'])
        print("Timestamp:",note['timestamp'])
        try:
            print("Link to wikipedia:",note['link'])
        except:
            pass
        print("-----------------------------------")
        count += 1
    print("\n")

#main function 
def main():
    try:
        #infinite loop before 0
        while True:

            #user choice from menu
            user_choice = 0
            user_choice = menu()

            #closing the client
            if(user_choice == 0):
                print('Closing...')
                break

            #wants to write a new topic
            elif(user_choice == 1):

                #getting the user input
                user_input = get_user_input()

                try: #network error
                    #sending the data to server
                    success = proxy.server_get_inputs(user_input)

                    #if server was successful
                    if(success):
                        print('Topic added')
                    else: #server error
                        print('A problem occured')
                except ConnectionRefusedError:
                    print('Could not add note. Please try again\n')

            #wants to look for a topic
            elif(user_choice == 2):

                #getting input
                topic_name = input('Give a topic name: ')

                #getting topics from server
                try: #network error
                    all_topics = proxy.get_contents(topic_name)
                    
                    if(len(all_topics)>0):#server error or no topic
                        #showing the notes  
                        show_topic_notes(all_topics,topic_name)
                    else:
                        print('No notes found for that topic\n')
                except ConnectionRefusedError:
                    print('Could not get the topic notes. Please try again\n')

            #wants to see wikipedia data
            elif (user_choice == 3):

                #input
                wikipedia_term = input('Give a wikipedia searchterm: ')

                #getting wikipedia search result from server
                try: #network error
                    wikipedia_data = proxy.get_wikipedia_data(wikipedia_term,10)
                    
                    #did not have any data or something went wrong on server
                    if(len(wikipedia_data[3]) == 0): 
                        print('No data for that searchterm\n')
                    
                    #had data
                    else:

                        #show the data
                        topic_list = show_wikipedia_data(wikipedia_data)

                        #wants to add link to topic
                        if(len(topic_list)>0):

                            #sending link to server to be added to xml
                            success = proxy.add_wikipedia_topic(topic_list)

                            #worked
                            if(success):
                                print("Link added to the Topic\n")
                            #did not work
                            else:
                                print("Topic was not found\n")
                except ConnectionRefusedError:
                    print('Could not connect to wikipedia. Please try again\n')
            
                
            #wrong value
            else:
                print('Only 0,1,2,3 can be given. Please try again\n')
    except KeyboardInterrupt:
        print('Closing the app')

main()