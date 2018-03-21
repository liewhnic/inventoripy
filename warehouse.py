#!/usr/bin/env python

### delete with name (display all before asking to delete)
### search with description or barcode (display all alternatives), select alternative, cmd (delete, quit, print barcode(for item, location))


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
        name=raw_input("Give new team\n")
        description=raw_input("Enter a description\n")
        team=Team(name, description)
        if team not in self.data["teams"]:
            #take picture
            self.data["teams"].add(team)
        else:
            print "Team already in database"
        print "Teams: ", self.data["teams"]

    def add_item_from_keyboard(self, nopic=False):
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

        if not nopic:
            items_picture_dir=self.pictures_dir+Item.pictures_subdir
            if not check_create_dir(items_picture_dir):
                exit(1)
            picture_filename=name+".jpg"
            print "Picture filename", picture_filename

            capture_picture(items_picture_dir+picture_filename)
        else:
            picture_filename=None

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

    def __str__(self):
        return("users: "+str(self.data["users"])+"\n"
               +"teams: "+str(self.data["teams"])+"\n"
               +"locations: "+str(self.data["locations"])+"\n"
               +"items: "+str(self.data["items"]))

class Item:
    pictures_subdir="items/"
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

    def show_pic(self, pictures_dir):
        show_picture(pictures_dir+self.pictures_subdir+self.picture_filename)

    def __repr__(self):
        return(self.name+self.description+str(self.placa))

    def __str__(self):
        return("\n"+self.name+", "+"Description: "+self.description+", "+"Location: "+self.location.name+", "+"Guardian: "+self.guardian.name+", "+"State: "+self.working_state+", Picture: "+str(self.picture_filename)+", Barcode: "+str(self.barcode_id))

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
    parser.add_argument("-s", "--show", help="Print Database", action="store_true")
    parser.add_argument("-b", "--barcode", help="Print barcode", action="store_true")
    parser.add_argument("--nopic", help="No picture", action="store_true")
    parser.add_argument("-p", "--pictures_dir", help="pictures_directory", default="warehouse/pictures/")
    parser.add_argument("-k", "--keyword", help="Remove or search keywords")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--store", action="store_true")
    args=parser.parse_args()

    home_dir= expanduser("~")
    pictures_dir=home_dir+"/"+args.pictures_dir
    print "Pictures dir: ", pictures_dir
    if not check_create_dir(pictures_dir):
        print "Error"
        exit(1)

    wh=Warehouse(pictures_dir)
    pygame.init()
    pygame.camera.init()
    pygame.display.init()


    if args.load:
        print "Loading"
        wh.load_from_file("test.dat")



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
                        if isinstance(found, Location):
                            print "It is a location"
                            os.system("(bincodes -e 39 -b 1 "+str(found.barcode_id)+" | line2bitmap; textlabel \" "+str(found.name)+"\") | pt1230 -c -m -b -d /dev/usb/lp1")
                        if isinstance(found, Item):
                            os.system("(textlabel \" \"; bincodes -e 39 -b 1 "+str(found.barcode_id)+" | line2bitmap; textlabel \" \") | pt1230 -c -m -b -d /dev/usb/lp1")
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
                    cmd2=raw_input("Press desired command: r: remove, p: print barcode\n")
                    if cmd2=="r":
                        print "Removing"
                        wh.remove_item_location(entry)
                    if cmd2=="p":
                        print "Types: ", type(entry), Location
                        if isinstance(entry,Location):
                            print "It is a location"
                            os.system("(bincodes -e 39 -b 1 "+str(entry.barcode_id)+" | line2bitmap; textlabel \" "+str(entry.name)+"\") | pt1230 -c -m -b -d /dev/usb/lp1")
                        if isinstance(entry, Item):
                            print "It is an Item"
                            os.system("(textlabel \" \"; bincodes -e 39 -b 1 "+str(entry.barcode_id)+" | line2bitmap; textlabel \" \") | pt1230 -c -m -b -d /dev/usb/lp1")
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
                os.system("(bincodes -e 39 -b 1 "+str(location.barcode_id)+" | line2bitmap; textlabel \" "+str(location.name)+"\") | pt1230 -c -m -b -d /dev/usb/lp1")
        elif args.item:
            print "Adding item"
            item=wh.add_item_from_keyboard(nopic=args.nopic)
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

if __name__=="__main__":
    main()
