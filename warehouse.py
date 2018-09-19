#!/usr/bin/env python

#add feed to cut tape

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
from time import sleep

def read_number(data=""):
    print data
    while True:
        try:
            val=int(raw_input())
        except ValueError:
            print "Not a number, try again"
        else:
            break
    return(val)

def check_create_dir(mydir):
    if not exists(mydir):
        if isfile(mydir):
            print "Error: Desired directory is actually a file, please remove this file before continuing"
            return(False)
        else:
            print "Creating desired directory"
            makedirs(mydir)
            return(True)
    else:
        if not isfile(mydir):
            return(True)
        else:
            print "Error: Desired directory is actually a file, please remove this file before continuing"
            return(False)

detected_barcode=None

def process_qr(data):
    os.system("beep -f 500 -l 60")
    print "Barcode detected: ", data
    global detected_barcode
    detected_barcode=data

def detect_barcode():
    qr=qrtools.QR()
    qr.decode_webcam(callback=process_qr)
    if detected_barcode:
        print "Detected barcode: ", detected_barcode
        return(int(detected_barcode))
    else:
        return(None)

def capture_picture(full_picture_filename):
    print "Taking picture"
    cam=pygame.camera.Camera("/dev/video0", (1280, 720))
    raw_input("Press enter when ready")
    ready=""
    while ready=="":
        cam.start()
        image=cam.get_image()
        cam.stop()

        pygame.image.save(image, full_picture_filename)
        display=pygame.display.set_mode((1280, 720), 0)
        display.blit(image, (0,0))
        pygame.display.flip()
        #sleep(2)
        ready=raw_input("Press \"y\" when satisfied. Press enter to repeat capture")

    pygame.display.quit()

def show_picture(full_picture_filename):
    try:
        image=pygame.image.load(full_picture_filename)
        display=pygame.display.set_mode((1280, 720), 0)
        display.blit(image, (0,0))
        pygame.display.flip()
        raw_input("Press enter to close window")
        pygame.display.quit()
    except:
        print "Error loading file"


class Warehouse(object):
    usage_functions=["unspecified", "hand tool", "electric tool", "electronic component", "raw metal", "raw plastic", "computer accesory"]
    working_states=["unknow", "good", "bad"]
    def __init__(self, config_dir="warehouse/", config_file="warehouse.dat"):
        self.config_dir=config_dir
        self.pictures_dir=config_dir+"pictures/"
        self.config_file=config_file
        self.data={
            "items": set(),
            "locations": set(),
            "users": set(),
            "teams": set(),
            "owners": set(),
            "free_barcode": 0
            }

    def search_item_barcode(self, barcode):
        for item in self.data["items"]:
            if item.barcode_id==barcode:
                return(item)
        return(None)

    def search_location_barcode(self, barcode):
        for location in self.data["locations"]:
            if location.barcode_id==barcode:
                return(location)
        return(None)

    def search_barcode(self, barcode):
        item=self.search_item_barcode(barcode)
        if item:
            print "Found item: "
            return(item)
        else:
            location=self.search_location_barcode(barcode)
            if location:
                print "Found location: "
                return(location)
            else:
                print "No item or location found"
                return(None)

    def remove_item_location(self, data):
        if data in self.data["items"]:
            self.data["items"].remove(data)
        else:
            if data in self.data["locations"]:
                self.data["locations"].remove(data)
            else:
                print "Error: data not found neither in items nor in locatiosn"

    def search_keyword(self, keyword):
        print "searching for entries in database with keyword: ", keyword
        res=[]
        for table in self.data:
            print "Table: ", table
            if type(self.data[table])==type(set()):
                for entry in self.data[table]:
                    print "Entry: ", entry
                    entry_str=repr(entry).lower()
                    print "Entry string: ", entry_str
                    if keyword.lower() in entry_str:
                        print "Found!!!"
                        res.append(entry)
        return(res)

    def add_user_from_keyboard(self, nopic=False):
        print "Adding new user"
        name=""
        while len(name)==0:
            name=raw_input("Give new username\n")

        if not nopic:
            users_picture_dir=self.pictures_dir+User.pictures_subdir
            if not check_create_dir(users_picture_dir):
                exit(1)
            picture_filename=name+".jpg"
            print "Picture filename", picture_filename

            capture_picture(users_picture_dir+picture_filename)
        else:
            picture_filename=None

        user=User(name, picture_filename=picture_filename)

        if user not in self.data["users"]:
            #take picture
            self.data["users"].add(user)
        else:
            print "User already in database"
        print "Users: ", self.data["users"]

    def add_location_from_keyboard(self, nopic=False):
        print "Adding new location"
        name=""
        while len(name)==0:
            name=raw_input("Give new location\n")

        if not nopic:
            locations_picture_dir=self.pictures_dir+Location.pictures_subdir
            if not check_create_dir(locations_picture_dir):
                exit(1)
            picture_filename=name+".jpg"
            print "Picture filename", picture_filename

            capture_picture(locations_picture_dir+picture_filename)
        else:
            picture_filename=None

        description=raw_input("Enter a description\n")
        location=Location(name, description, picture_filename=picture_filename)
        if location not in self.data["locations"]:
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
        name=""
        while len(name)==0:
            name=raw_input("Give new team\n")
        description=raw_input("Enter a description\n")
        team=Team(name, description)
        if team not in self.data["teams"]:
            #take picture
            self.data["teams"].add(team)
        else:
            print "Team already in database"
        print "Teams: ", self.data["teams"]

    def add_owner_from_keyboard(self):
        print "Adding new owner"
        name=""
        while len(name)==0:
            name=raw_input("Give new owner\n")
        description=raw_input("Enter a description\n")
        owner=Owner(name, description)
        if owner not in self.data["owners"]:
            #take picture
            self.data["owners"].add(owner)
        else:
            print "Owner already in database"
        print "Owners: ", self.data["owners"]

    def add_item_from_keyboard(self, nopic=False):
        print "Adding new item"
        name=""
        while len(name)==0:
            name=raw_input("Give new item name\n")
        description=raw_input("Description:\n")
        print "Select location number\n"
        locations=[]
        for i, location in enumerate(self.data["locations"]):
            locations.append(location)
            print i, ": ", location
        #location (select from posible locations)
        location_n=read_number()
        location=locations[location_n]
        print "Selected location: ", location
        usage_frequency=read_number("Select usage frequency (0: low, 1: medium, 2: high)\n")

        print "Select team\n"
        teams=[]
        for i, team in enumerate(self.data["teams"]):
            teams.append(team)
            print i, ": ", team
        #team (select from posible teams)
        team_n=read_number()
        team=teams[team_n]
        print "Selected team: ", team

        print "Select owner\n"
        owners=[]
        for i, owner in enumerate(self.data["owners"]):
            owners.append(owner)
            print i, ": ", owner
        #owner (select from posible owners)
        owner_n=read_number()
        owner=owners[owner_n]
        print "Selected owner: ", owner

        print "Select guardian (0: unspecified)\n"
        users=[]
        for i, user in enumerate(self.data["users"]):
            users.append(user)
            print i, ": ", user
        #guardian (select from posible users)
        user_n=read_number()
        guardian=users[user_n]
        print "Selected guardian: ", guardian

        print "Select usage function (0: unspecified)\n"
        for i, usage_function in enumerate(self.usage_functions):
            print i, ": ", usage_function
        #usage_function (select from posible usage_functions)
        usage_function_n=read_number()
        usage_function=self.usage_functions[usage_function_n]
        print "Selected usage_function: ", usage_function

        placa=read_number("Enter \"placa\":\n")
        # todo: check placa is not repeated

        print "Select working state (0: unknow)\n"
        for i, working_state in enumerate(self.working_states):
            print i, ": ", working_state
        working_state_n=read_number()
        working_state=self.working_states[working_state_n]
        print "Selected working state: ", working_state

        if working_state == "bad":
            working_state_description=raw_input("Enter a working state description:\n")
        else:
            working_state_description=""

        if not nopic:
            items_picture_dir=self.pictures_dir+Item.pictures_subdir
            if not check_create_dir(items_picture_dir):
                exit(1)
            picture_filename=name+".jpg"
            print "Picture filename", picture_filename

            capture_picture(items_picture_dir+picture_filename)
        else:
            picture_filename=None

        item=Item(self.data, name, description, location, usage_frequency, team, guardian, owner, usage_function, working_state, working_state_description=working_state_description, placa=placa, picture_filename=picture_filename)
        if item not in self.data["items"]:
            item.barcode_id=self.data["free_barcode"]
            print "Barcode id: ", item.barcode_id
            self.data["free_barcode"]+=1
            self.data["items"].add(item)
            return(item)
        else:
            print "Item already in database"
        print "Items: ", self.data["items"]

    def load_from_file(self):
        f=open(self.config_dir+self.config_file,'rb')
        data=pickle.load(f)
        f.close()
        self.data=data

    def store_to_file(self):
        f=open(self.config_dir+self.config_file, "wb")
        pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def __str__(self):
        return("users: "+str(self.data["users"])+"\n"
               +"teams: "+str(self.data["teams"])+"\n"
               +"owners: "+str(self.data["owners"])+"\n"
               +"locations: "+str(self.data["locations"])+"\n"
               +"items: "+str(self.data["items"]))

class Item:
    pictures_subdir="items/"
    def __init__(self, parent, name, description, location, usage_frequency, team, guardian, owner, usage_function, working_state, stored=True, placa=None, working_state_description="All fine", picture_filename=None):
        self.parent=parent
        self.name=name
        self.description=description
        self.location=location
        self.usage_frequency=usage_frequency
        self.team=team
        self.guardian=guardian
        self.owner=owner
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

    def show_pic(self, pictures_dir):
        show_picture(pictures_dir+self.pictures_subdir+self.picture_filename)

    def __repr__(self):
        return(self.name+self.description+str(self.placa))

    def __str__(self):
        return("\n"+self.name+", "+"Description: "+self.description+", "+"Location: "+self.location.name+", "+"Guardian: "+self.guardian.name+", "+"Owner: "+self.owner.name+", "+"State: "+self.working_state+", Picture: "+str(self.picture_filename)+", Barcode: "+str(self.barcode_id))

class Location:
    pictures_subdir="locations/"
    def __init__(self, name, description, picture_filename=None):
        self.name=name
        self.description=description
        self.picture_filename=picture_filename
        self.barcode_id=None

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def show_pic(self, pictures_dir):
        show_picture(pictures_dir+self.pictures_subdir+self.picture_filename)

    def __repr__(self):
        return(self.name+self.description)

    def __str__(self):
        return("\n"+self.name+", "+"Description: "+str(self.description)+", Picture: "+str(self.picture_filename)+", Barcode: "+str(self.barcode_id))

class Team:
    def __init__(self, name, description):
        self.name=name
        self.description=description

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def __repr__(self):
        return(self.name+self.description)

    def __str__(self):
        return("\n"+self.name+", "+"Description: "+str(self.description))

class Owner:
    def __init__(self, name, description):
        self.name=name
        self.description=description

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def __repr__(self):
        return(self.name+self.description)

    def __str__(self):
        return("\n"+self.name+", "+"Description: "+str(self.description))

class User:
    pictures_subdir="users/"
    def __init__(self, name, picture_filename=None):
        self.name=name
        self.picture_filename=picture_filename
        self.punishment=None

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

    def show_pic(self, pictures_dir):
        show_picture(pictures_dir+self.pictures_subdir+self.picture_filename)

    def __repr__(self):
        return(self.name)

    def __str__(self):
        return("\n"+self.name+", "+"Punishment: "+str(self.punishment)+", Picture: "+str(self.picture_filename))

def main():
    parser=argparse.ArgumentParser()
    # add : (user, location, item, team)
    parser.add_argument("-a", "--add", help="add something to database", action="store_true")
    parser.add_argument("--search", help="search something from database", action="store_true")
    parser.add_argument("-u", "--user", help="add user to database", action="store_true")
    parser.add_argument("-l", "--location", help="add location to database", action="store_true")
    parser.add_argument("-i", "--item", help="add item to database", action="store_true")
    parser.add_argument("-t", "--team", help="add team to database", action="store_true")
    parser.add_argument("-o", "--owner", help="add owner to database", action="store_true")
    parser.add_argument("-s", "--show", help="Print Database", action="store_true")
    parser.add_argument("-b", "--barcode", help="Print/search barcode", action="store_true")
    parser.add_argument("--nopic", help="No picture", action="store_true")
    parser.add_argument("--pname", help="Print Name", action="store_true")
    parser.add_argument("--powner", help="Print Owner", action="store_true")
    parser.add_argument("-f", "--feedprinter", help="Feed printer for cutting", action="store_true")
    parser.add_argument("-c", "--config_dir", help="config_directory", default="warehouse/")
    parser.add_argument("-k", "--keyword", help="Remove or search keywords")
    parser.add_argument("-d", "--device", help="Printer device filename",default= "/dev/usb/lp0")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--store", action="store_true")
    args=parser.parse_args()

    home_dir= expanduser("~")
    config_dir=home_dir+"/"+args.config_dir
    pictures_dir=config_dir+"pictures/"
    print "Pictures dir: ", pictures_dir
    if not check_create_dir(config_dir):
        print "Error"
        exit(1)
    if not check_create_dir(pictures_dir):
        print "Error"
        exit(1)

    wh=Warehouse(config_dir=config_dir)
    pygame.init()
    pygame.camera.init()
    pygame.display.init()


    if args.load:
        print "Loading"
        wh.load_from_file()



    if args.search:
        print "search from database"
        if args.barcode:
            print "Using barcode"
            detected_barcode=detect_barcode()
            if detected_barcode:
                print "Detected barcode: ", detected_barcode
                found=wh.search_barcode(detected_barcode)
                if found:
                    print found
                    found.show_pic(wh.pictures_dir)
                    cmd=raw_input("Press desired command: r: remove, p: print barcode\n")
                    if cmd=="r":
                        print "Removing"
                        wh.remove_item_location(found)
                    if cmd=="p":
                        while not os.path.exists(args.device):
                            print "Connect device to: ", args.device
                            sleep(2)
                        if isinstance(found, Location):
                            print "It is a location"
                            os.system("(bincodes -e 39 -b 1 "
                                      +str(found.barcode_id)+
                                      " | line2bitmap; textlabel \" "+
                                      str(found.name)
                                      +"\") | pt1230 -c -m -b -d "+args.device)
                        if isinstance(found, Item):
                            text=""
                            if found.placa != 0:
                                text+=found.name+","+found.owner.name
                            else:
                                if args.pname:
                                    text+=found.name
                                if args.pname and args.powner:
                                    text+=","
                                if args.powner:
                                    text+=found.owner.name
                            os.system("(textlabel \" \"; bincodes -e 39 -b 1 "
                                      +str(found.barcode_id)
                                      +" | line2bitmap; textlabel --width 32 \" "+str(text)+"\") | pt1230 -c -m -b -d "+
                                      args.device)
                    else:
                        print "Quitting"
                else:
                    print "Barcode not found in database"
            else:
                print "No barcode detected"
        elif args.keyword:
            print "Searching for keyword: ", args.keyword
            res=wh.search_keyword(args.keyword)
            if len(res)==0:
                print "No results"
            else:
                print "Search results:"
                for i, j in enumerate(res):
                    print i, ": ", j
                cmd=raw_input("Press the entry number to select from database or press enter to quit\n")
                if cmd!="":
                    entry=res[int(cmd)]
                    print "Selected entry: ", int(cmd), entry
                    entry.show_pic(wh.pictures_dir)
                    cmd2=raw_input("Press desired command: r: remove, p: print barcode\n")
                    if cmd2=="r":
                        print "Removing"
                        wh.remove_item_location(entry)
                    if cmd2=="p":
                        print "Types: ", type(entry), Location
                        while not os.path.exists(args.device):
                            print "Connect device to: ", args.device
                            sleep(2)
                        if isinstance(entry,Location):
                            print "It is a location"
                            os.system("(bincodes -e 39 -b 1 "+str(entry.barcode_id)+" | line2bitmap; textlabel \" "
                                      +str(entry.name)
                                      +"\") | pt1230 -c -m -b -d "+args.device)
                        if isinstance(entry, Item):
                            print "It is an Item"
                            text=""
                            if entry.placa != 0:
                                text+=entry.name+","+entry.owner.name
                            else:
                                if args.pname:
                                    text+=entry.name
                                if args.pname and args.powner:
                                    text+=","
                                if args.powner:
                                    text+=entry.owner.name
                            os.system("(textlabel \" \"; bincodes -e 39 -b 1 "+str(entry.barcode_id)
                                      +" | line2bitmap; textlabel --width 32 \" "+str(text)+"\") | pt1230 -c -m -b -d "+
                                      args.device)
                    else:
                        print "Quitting"
                else:
                    print "Quitting"

        else:
            print "Not removing"


    if args.add:
        if args.user:
            print "Adding user"
            wh.add_user_from_keyboard(nopic=args.nopic)
        elif args.location:
            print "Adding location"
            location=wh.add_location_from_keyboard()
            if args.barcode and location:
                print "Printing location and barcode: ", location.barcode_id
                while not os.path.exists(args.device):
                    print "Connect device to: ", args.device
                    sleep(2)
                os.system("(bincodes -e 39 -b 1 "+str(location.barcode_id)+" | line2bitmap; textlabel \" "
                          +str(location.name)+"\") | pt1230 -c -m -b -d "
                          +args.device)
        elif args.item:
            print "Adding item"
            item=wh.add_item_from_keyboard(nopic=args.nopic)
            if args.barcode and item:
                print "Printing barcode: ", item.barcode_id
                while not os.path.exists(args.device):
                    print "Connect device to: ", args.device
                    sleep(2)
                text=""
                if item.placa != 0:
                    text+=item.name+","+item.owner.name
                else:
                    if args.pname:
                        text+=item.name
                    if args.pname and args.powner:
                        text+=","
                    if args.powner:
                        text+=item.owner.name
                os.system("(textlabel \" \"; bincodes -e 39 -b 1 "+str(item.barcode_id)+
                          " | line2bitmap; textlabel --width 32 \" "+str(text)+"\") | pt1230 -c -m -b -d "
                          +args.device)
        elif args.team:
            print "Adding team"
            wh.add_team_from_keyboard()

        elif args.owner:
            print "Adding owner"
            wh.add_owner_from_keyboard()

    if args.store:
        print "Storing"
        wh.store_to_file()

    if args.show:
        if args.barcode:
            print "Print item or location"
            detected_barcode=detect_barcode()
            if detected_barcode:
                found=wh.search_barcode(detected_barcode)
                if found:
                    print found
                    found.show_pic(wh.pictures_dir)
                else:
                    print "Error: No item or location found"
            else:
                print "Error"
        else:
            print "Printing database"
            print wh

    if args.feedprinter:
        os.system("textlabel \"       \" | pt1230 -c -m -b -d /dev/usb/lp1")

if __name__=="__main__":
    main()
