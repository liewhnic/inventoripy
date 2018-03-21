#!/usr/bin/env python

import argparse
import pickle
from os.path import expanduser, exists, isfile
from os import makedirs
import pygame
import pygame.camera
import pygame.image
import pygame.display
from time import sleep
import os
import hashlib
import qrtools

def check_create_dir(mydir):
    if not exists(mydir):
        if isfile(mydir):
            print "Desired directory is actually a file, please remove this file before continuing"
            return(False)
        else:
            print "Creating desired directory"
            makedirs(mydir)
            return(True)
    else:
        if not isfile(mydir):
            return(True)
        else:
            print "Desired directory is actually a file, please remove this file before continuing"
            return(False)

detected_barcode=None

def process_qr(data):
    os.system("beep -f 500 -l 60")
    print "Barcode detected: ", data
    global detected_barcode
    detected_barcode=data


class Warehouse(object):
    usage_functions=["unspecified", "hand tool", "electric tool", "electronic component", "raw metal", "raw plastic", "computer accesory"]
    working_states=["unknow", "good", "bad"]
    def __init__(self, pictures_dir):
        self.pictures_dir=pictures_dir
        self.data={
            "items": set(),
            "locations": set(),
            "users": set(),
            "teams": set(),
            "free_barcode": 0
            }

    def search_item_barcode(self, barcode):
        for item in self.data["items"]:
            print "Item: ", item.name, " barcode: ", item.barcode_id
            if item.barcode_id==barcode:
                return(item)
        return(None)

    def search_location_barcode(self, barcode):
        for location in self.data["locations"]:
            print "Location: ", location.name, " barcode: ", location.barcode_id
            if location.barcode_id==barcode:
                return(location)
        return(None)

    def add_user_from_keyboard(self):
        print "Adding new user"
        name=raw_input("Give new username\n")

        print "Taking picture"
        cam=pygame.camera.Camera("/dev/video0", (1280, 720))
        cam.start()
        raw_input("Press enter when ready")
        image=cam.get_image()
        picture_filename=self.pictures_dir+"users/"
        if not check_create_dir(picture_filename):
            exit(1)
        picture_filename+=name+".jpg"

        print "Picture filename", picture_filename
        pygame.image.save(image, picture_filename)
        display=pygame.display.set_mode((1280, 720), 0)
        display.blit(image, (0,0))
        pygame.display.flip()
        #sleep(2)
        raw_input("Press enter to close window")
        pygame.display.quit()

        user=User(name, picture_filename=picture_filename)

        if user not in self.data["users"]:
            #take picture
            self.data["users"].add(user)
        else:
            print "User already in database"
        print "Users: ", self.data["users"]

    def add_location_from_keyboard(self):
        print "Adding new location"
        name=raw_input("Give new location\n")
        description=raw_input("Enter a description\n")
        location=Location(name, description)
        if location not in self.data["locations"]:
            #take picture
            location.barcode_id=self.data["free_barcode"]
            print "Barcode id: ", location.barcode_id
            self.data["free_barcode"]+=1
            self.data["locations"].add(location)
            return(location)
        else:
            print "Location already in database"
        print "Locations: ", self.data["locations"]

    def add_team_from_keyboard(self):
        print "Adding new team"
        name=raw_input("Give new team\n")
        description=raw_input("Enter a description\n")
        team=Team(name, description)
        if team not in self.data["teams"]:
            #take picture
            self.data["teams"].add(team)
        else:
            print "Team already in database"
        print "Teams: ", self.data["teams"]

    def add_item_from_keyboard(self):
        print "Adding new item"
        name=raw_input("Give new item name\n")
        description=raw_input("Description:\n")
        print "Select location number\n"
        locations=[]
        for i, location in enumerate(self.data["locations"]):
            locations.append(location)
            print i, ": ", location
        #location (select from posible locations)
        location_n=int(raw_input())
        location=locations[location_n]
        print "Selected location: ", location
        usage_frequency=int(raw_input("Select usage frequency (0: low, 1: medium, 2: high)\n"))

        print "Select team (0: unspecified)\n"
        teams=[]
        for i, team in enumerate(self.data["teams"]):
            teams.append(team)
            print i, ": ", team
        #team (select from posible teams)
        team_n=int(raw_input())
        team=teams[team_n]
        print "Selected team: ", team

        print "Select guardian (0: unspecified)\n"
        users=[]
        for i, user in enumerate(self.data["users"]):
            users.append(user)
            print i, ": ", user
        #guardian (select from posible users)
        user_n=int(raw_input())
        guardian=users[user_n]
        print "Selected guardian: ", guardian

        print "Select usage function (0: unspecified)\n"
        for i, usage_function in enumerate(self.usage_functions):
            print i, ": ", usage_function
        #usage_function (select from posible usage_functions)
        usage_function_n=int(raw_input())
        usage_function=self.usage_functions[usage_function_n]
        print "Selected usage_function: ", usage_function

        placa=int(raw_input("Enter \"placa\":\n"))
        # todo: check placa is not repeated

        print "Select working state (0: unknow)\n"
        for i, working_state in enumerate(self.working_states):
            print i, ": ", working_state
        working_state_n=int(raw_input())
        working_state=self.working_states[working_state_n]
        print "Selected working state: ", working_state

        if working_state == "bad":
            working_state_description=raw_input("Enter a working state description:\n")
        else:
            working_state_description=""

        print "Taking picture"
        cam=pygame.camera.Camera("/dev/video0", (1280, 720))
        cam.start()
        raw_input("Press enter when ready")
        image=cam.get_image()
        picture_filename=self.pictures_dir+"items/"
        if not check_create_dir(picture_filename):
            exit(1)
        picture_filename+=name+".jpg"

        print "Picture filename", picture_filename
        pygame.image.save(image, picture_filename)
        display=pygame.display.set_mode((1280, 720), 0)
        display.blit(image, (0,0))
        pygame.display.flip()
        #sleep(2)
        raw_input("Press enter to close window")
        pygame.display.quit()

        item=Item(self.data, name, description, location, usage_frequency, team, guardian, usage_function, working_state, working_state_description=working_state_description, placa=placa, picture_filename=picture_filename)
        if item not in self.data["items"]:
            item.barcode_id=self.data["free_barcode"]
            print "Barcode id: ", item.barcode_id
            self.data["free_barcode"]+=1
            self.data["items"].add(item)
            return(item)
        else:
            print "Item already in database"
        print "Items: ", self.data["items"]

    def load_from_file(self, filename):
        f=open(filename,'rb')
        data=pickle.load(f)
        f.close()
        self.data=data

    def store_to_file(self, filename):
        f=open(filename, "wb")
        pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def __repr__(self):
        return("users: "+repr(self.data["users"])+"\n"
               +"teams: "+repr(self.data["teams"])+"\n"
               +"locations: "+repr(self.data["locations"])+"\n"
               +"items: "+repr(self.data["items"]))

class Item:
    def __init__(self, parent, name, description, location, usage_frequency, team, guardian, usage_function, working_state, stored=True, placa=None, working_state_description="All fine", picture_filename=None):
        self.parent=parent
        self.name=name
        self.description=description
        self.location=location
        self.usage_frequency=usage_frequency
        self.team=team
        self.guardian=guardian
        self.usage_function=usage_function
        self.stored=stored
        self.placa=placa
        self.previous_users=[]
        self.cur_user=[]
        self.working_state=working_state
        self.working_state_description=working_state_description
        self.picture_filename=picture_filename
        self.barcode_id=None

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def __repr__(self):
        print "Repr: "
        print self.name, self.description, self.location.name, self.guardian.name, self.working_state
        return("\n"+self.name+", "+"Description: "+self.description+", "+"Location: "+self.location.name+", "+"Guardian: "+self.guardian.name+", "+"State: "+self.working_state+", Picture: "+self.picture_filename.split("/")[-1])

class Location:
    def __init__(self, name, description, picture_filename=None):
        self.name=name
        self.description=description
        self.picture_filename=picture_filename
        self.barcode_id=None

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def __repr__(self):
        return("\n"+self.name+", "+"Description: "+str(self.description))

class Team:
    def __init__(self, name, description):
        self.name=name
        self.description=description

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def __repr__(self):
        return("\n"+self.name+", "+"Description: "+str(self.description))

class User:
    def __init__(self, name, picture_filename=None):
        self.name=name
        self.picture_filename=picture_filename
        self.punishment=None

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))


    def __repr__(self):
        return("\n"+self.name+", "+"Punishment: "+str(self.punishment))

def main():
    parser=argparse.ArgumentParser()
    # add : (user, location, item, team)
    parser.add_argument("-a", "--add", help="add something to database", action="store_true")
    parser.add_argument("-u", "--user", help="add user to database", action="store_true")
    parser.add_argument("-l", "--location", help="add location to database", action="store_true")
    parser.add_argument("-i", "--item", help="add item to database", action="store_true")
    parser.add_argument("-t", "--team", help="add team to database", action="store_true")
    parser.add_argument("-s", "--show", help="Print Database", action="store_true")
    parser.add_argument("-b", "--barcode", help="Print barcode", action="store_true")
    parser.add_argument("-p", "--pictures_dir", help="pictures_directory", default="warehouse/pictures/")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--store", action="store_true")
    args=parser.parse_args()

    home_dir= expanduser("~")
    pictures_dir=home_dir+"/"+args.pictures_dir
    print "Pictures dir: ", pictures_dir
    if not check_create_dir(pictures_dir):
        exit(1)

    wh=Warehouse(pictures_dir)
    pygame.init()
    pygame.camera.init()
    pygame.display.init()

    if args.load:
        print "Loading"
        wh.load_from_file("test.dat")

    if args.add:
        if args.user:
            print "Adding user"
            wh.add_user_from_keyboard()
        elif args.location:
            print "Adding location"
            location=wh.add_location_from_keyboard()
            if args.barcode and location:
                print "Printing location and barcode: ", location.barcode_id
                os.system("(bincodes -e 39 -b 1 "+str(location.barcode_id)+" | line2bitmap; textlabel \" "+str(location.name)+"\") | pt1230 -c -m -b -d /dev/usb/lp1")
        elif args.item:
            print "Adding item"
            item=wh.add_item_from_keyboard()
            if args.barcode and item:
                print "Printing barcode: ", item.barcode_id
                os.system("(textlabel \" \"; bincodes -e 39 -b 1 "+str(item.barcode_id)+" | line2bitmap; textlabel \" \") | pt1230 -c -m -b -d /dev/usb/lp1")
        elif args.team:
            print "Adding team"
            wh.add_team_from_keyboard()

    if args.store:
        print "Storing"
        wh.store_to_file("test.dat")

    if args.show:
        if args.barcode:
            print "Print item or location"
            qr=qrtools.QR()
            qr.decode_webcam(callback=process_qr)
            if detected_barcode:
                print "Detected barcode: ", detected_barcode
                item=wh.search_item_barcode(int(detected_barcode))
                if item:
                    print "Found item: ", item
                else:
                    print "Barcode item not found, searching for location barcode"
                    location=wh.search_location_barcode(int(detected_barcode))
                    if location:
                        print "Found location: ", location
                    else:
                        print "Barcode location not found"
            else:
                print "Error"
        else:
            print "Printing database"
            print wh

if __name__=="__main__":
    main()
