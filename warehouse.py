#!/usr/bin/env python

import argparse
import pickle

class Warehouse:
    def __init__(self):
        self.data={
            "items": set(),
            "locations": set(),
            "users": set(),
            "teams": set()
            }

    def add_user_from_keyboard(self):
        print "Adding new user"
        name=raw_input("Give new username\n")
        user=User(name)
        if user not in self.data["users"]:
            #take picture
            self.data["users"].add(user)
        else:
            print "User already in database"
        print "Users: ", self.data["users"]

    def add_location_from_keyboard(self):
        print "Adding new location"
        name=raw_input("Give new location\n")
        location=Location(name)
        if location not in self.data["locations"]:
            #take picture
            self.data["locations"].add(location)
        else:
            print "Location already in database"
        print "Locations: ", self.data["locations"]

    def add_team_from_keyboard(self):
        print "Adding new team"
        name=raw_input("Give new team\n")
        team=Team(name)
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
        #location (select from posible locations)
        item=Item(self.data, name, )
        if item not in self.data["items"]:
            #take picture
            self.data["items"].add(item)
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

class Item:
    def __init__(self, parent, name, description, location, usage_frequency, team, guardian, usage_function, stored=True, placa=None, working_state=True, working_state_description="All fine", picture_filename=None):
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

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

class Location:
    def __init__(self, name, description, picture_filename=None):
        self.name=name
        self.description=description
        self.picture_filename=picture_filename

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

class Team:
    def __init__(self, name, description):
        self.name=name
        self.description=description

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, other):
        return(hash(self)==hash(other))

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
        return("\nName: "+self.name+", "+"Punishment: "+str(self.punishment))

def main():
    parser=argparse.ArgumentParser()
    # add : (user, location, item, team)
    parser.add_argument("-a", "--add", help="add something to database", action="store_true")
    parser.add_argument("-u", "--user", help="add user to database", action="store_true")
    parser.add_argument("-l", "--location", help="add location to database", action="store_true")
    parser.add_argument("-i", "--item", help="add item to database", action="store_true")
    parser.add_argument("-t", "--team", help="add team to database", action="store_true")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--store", action="store_true")
    args=parser.parse_args()

    wh=Warehouse()

    if args.load:
        print "Loading"
        wh.load_from_file("test.dat")

    if args.add:
        if args.user:
            print "Adding user"
            wh.add_user_from_keyboard()
        elif args.location:
            print "Adding location"
        elif args.item:
            print "Adding item"
        elif args.team:
            print "Adding team"

    if args.store:
        print "Storing"
        wh.store_to_file("test.dat")

if __name__=="__main__":
    main()
