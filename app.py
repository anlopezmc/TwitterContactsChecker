# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
import twitter
from xml.etree import ElementTree
import config # File with the parameters to connect to twitter API.

def download_contacts(screen_name, destination_folder):
    """ Method to downloads 'followers' and 'following' of an user given by 'screen_name' in a .xml file.

    :type screen_name: str
    :param screen_name: Name of the user in twitter (name after '@').
    :type destination_folder: str
    :param destination_folder: Path of the folder where save the downloaded .xml file.
    """
    # Check the type of the parameters.
    if type(screen_name) is not str:
        raise TypeError("Parameter 'screen_name' must be a str.")
    if type(destination_folder) is not str:
        raise TypeError("Parameter 'destination_folder' must be a str.")
    # Connect to Twitter API.
    print("Connecting to Twitter API.")
    api = twitter.Api(consumer_key = config.api_key,
                    consumer_secret = config.api_secret_key,
                    access_token_key = config.access_token,
                    access_token_secret = config.access_token_secret,
                    tweet_mode = 'extended') # This returns an object of type "twitter.Api".
    try:
        # Check if connection was ok.
        verified_user = api.VerifyCredentials() # This returns an object of type "twitter.User".
        print("Connected to Twitter API as @" + verified_user.screen_name + ".")
        # Delete the first character of the parameter 'screen_name' if it is '@'.
        real_screen_name = screen_name
        if (real_screen_name[0] == '@'):
            real_screen_name = real_screen_name[1:]
        # Get the current user (object of type "twitter.User") according to 'real_screen_name'.
        print("Retrieving user @" + real_screen_name + ".")
        current_user = api.GetUser(screen_name=real_screen_name)
        # Retrieve 'followers' and 'following' of 'current_user'. Lists of objects of type "twitter.User".
        print("Retrieving 'followers' of @" + current_user.screen_name + ".")
        list_of_followers = api.GetFollowers(screen_name=current_user.screen_name)
        print("Retrieving 'following' of @" + current_user.screen_name + ".")
        list_of_following = api.GetFriends(screen_name=current_user.screen_name)
    except twitter.error.TwitterError as error:
        print("** Twitter API exception **")
        print(error.message)
    except:
        print("** Other exception **")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        print(sys.exc_info()[2])
    else:
        # Get time.
        print("Getting datetime.")
        current_datetime = datetime.now()
        # Write the .xml file.
        print("Writing .xml file.")
        file = open(destination_folder + "/" + current_user.screen_name + "__" +
                    str(current_datetime.day) + "_" +
                    str(current_datetime.month) + "_" +
                    str(current_datetime.year) + "__" +
                    str(current_datetime.hour) + "_" +
                    str(current_datetime.minute) + "_" +
                    str(current_datetime.second) + ".xml", "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n\n')
        file.write('<user>\n\n')
        file.write('    <screen_name>@' + current_user.screen_name + '</screen_name>\n')
        file.write('    <id>' + str(current_user.id) + '</id>\n\n')
        file.write('    <followers count="' + str(len(list_of_followers)) + '">\n')
        for user in list_of_followers:
            file.write('        <user>\n')
            file.write('            <screen_name>@' + user.screen_name + '</screen_name>\n')
            file.write('            <id>' + str(user.id) + '</id>\n')
            file.write('        </user>\n')
        file.write('    </followers>\n\n')
        file.write('    <following count="' + str(len(list_of_following)) + '">\n')
        for user in list_of_following:
            file.write('        <user>\n')
            file.write('            <screen_name>@' + user.screen_name + '</screen_name>\n')
            file.write('            <id>' + str(user.id) + '</id>\n')
            file.write('        </user>\n')
        file.write('    </following>\n\n')
        file.write('</user>\n')
        file.close()
        print("Finished.")

def compare_contacts(old_xml_file, new_xml_file):
    """ Method to compare 2 .xml files of contacts (normally of the same user, one newer than the other).

    :type old_xml_file: str
    :param old_xml_file: Path of the first .xml file of contacts.
    :type new_xml_file: str
    :param new_xml_file: Path of thr second .xml file of contacts.
    """
    # Check the type of the parameters.
    if type(old_xml_file) is not str:
        raise TypeError("Parameter 'old_xml_file' must be a str.")
    if type(new_xml_file) is not str:
        raise TypeError("Parameter 'new_xml_file' must be a str.")    
    # Load .xml files.
    old_xml_file_root = ElementTree.parse(old_xml_file).getroot()
    new_xml_file_root = ElementTree.parse(new_xml_file).getroot()
    # Get the IDs of the 'followers' as a python 'set'.
    old_xml_file_followers = set()
    old_xml_file_followers_node = old_xml_file_root.find("followers")
    for node in old_xml_file_followers_node:
        old_xml_file_followers.add(node.find("screen_name").text)
    new_xml_file_followers = set()
    new_xml_file_followers_node = new_xml_file_root.find("followers")
    for node in new_xml_file_followers_node:
        new_xml_file_followers.add(node.find("screen_name").text)
    # Get the IDs of the 'following' as a python 'set'.
    old_xml_file_following = set()
    old_xml_file_following_node = old_xml_file_root.find("following")
    for node in old_xml_file_following_node:
        old_xml_file_following.add(node.find("screen_name").text)
    new_xml_file_following = set()
    new_xml_file_following_node = new_xml_file_root.find("following")
    for node in new_xml_file_following_node:
        new_xml_file_following.add(node.find("screen_name").text)
    # Analyze the 'followers' of the both files (unfollows and new followers).
    unfollows = old_xml_file_followers.difference(new_xml_file_followers)
    new_followers = new_xml_file_followers.difference(old_xml_file_followers)
    print("*****************************")
    print("********* UNFOLLOWS *********")
    print("*****************************")
    for user_name in unfollows:
        print(user_name)
    print("")
    print("*****************************")
    print("******* NEW FOLLOWERS *******")
    print("*****************************")
    for user_name in new_followers:
        print(user_name)
    print("")
    # Analyze the 'following' of the both files.
    unfollowing = old_xml_file_following.difference(new_xml_file_following)
    new_following = new_xml_file_following.difference(old_xml_file_following)
    print("*****************************")
    print("******** UNFOLLOWING ********")
    print("*****************************")
    for user_name in unfollowing:
        print(user_name)
    print("")
    print("*****************************")
    print("******* NEW FOLLOWING *******")
    print("*****************************")
    for user_name in new_following:
        print(user_name)
    print("")    

# Entry point.
if __name__ == "__main__":
    state = 0
    while (state != 3):
        if (state == 0):
            print("SELECT AN OPTION:")
            print("  [1] Download the last contacts for")
            print("  [2] Compare 2 .xml files")
            print("  [3] Exit")
            try:
                option = int(input("Option: "))
            except:
                print("\nIncorrect format.")
                state = 0
            else:
                if ((option >= 1) and (option <= 3)):
                    state = option
                else:
                    print("\nIncorrect option.")
                    state = 0
            print("##############################\n\n")
        elif (state == 1):
            try:
                input_screen_name = str(input("Enter username (or ENTER to exit): "))
            except:
                print("\nIncorrect format.")
            else:
                print("")
                if (len(input_screen_name) > 0) and (input_screen_name != '@'):
                    download_contacts(screen_name=input_screen_name, destination_folder="data/")
            state = 0
            print("##############################\n\n")
        elif (state == 2):
            try:
                old_xml_file_path = str(input("Enter the path of the old .xml file: "))
                new_xml_file_path = str(input("Enter the path of the new .xml file: "))
            except:
                print("\nIncorrect format.")
            else:
                if ((not os.path.isfile(old_xml_file_path)) or (not os.path.isfile(new_xml_file_path))):
                    print("\nFiles not found.")
                else:
                    print("")
                    compare_contacts(old_xml_file_path, new_xml_file_path)
            state = 0
            print("##############################\n\n")
