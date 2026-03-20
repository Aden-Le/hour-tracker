import pandas as pd
from collections import defaultdict

class Event:
    def __init__(self, name, classification, date, attendance):
        self.__name = name
        self.__classification = classification
        self.__date = date
        self.__attendance = attendance
        
    @property
    def name(self):
        return self.__name

    @property
    def classification(self):
        return self.__classification

    @property
    def date(self):
        return self.__date

    @property
    def attendance(self):
        return self.__attendance

class Student:
    def __init__(self, first_name, last_name, classification, family, event_list, row_number):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__classification = classification
        self.__family = family
        self.__event_list = event_list
        self.__row_number = row_number

    @property
    def first_name(self):
        return self.__first_name
    
    @property
    def last_name(self):
        return self.__last_name

    @property
    def classification(self):
        return self.__classification
    
    @property
    def family(self):
        return self.__family

    @property
    def event_list(self):
        return self.__event_list

    @event_list.setter
    def event_list(self, event):
        self.__event_list.append(event)
    
    @property
    def row_number(self):
        return self.__row_number

def import_names(input_file):
    #---------------------------------------------------------------
    # Load the CSV file
    input_data_frame = pd.read_csv(input_file, header=None, names=["First_name", "Last_name"])
    #---------------------------------------------------------------
    # Strip any whitespace around the names
    input_data_frame["First_name"] = input_data_frame["First_name"].str.strip()
    input_data_frame["Last_name"] = input_data_frame["Last_name"].str.strip()
    #---------------------------------------------------------------
    # Capitalize the first letter of each name
    input_data_frame["First_name"] = input_data_frame["First_name"].str.capitalize()
    input_data_frame["Last_name"] = input_data_frame["Last_name"].str.capitalize()
    #---------------------------------------------------------------
    # Return the new names DataFrame
    return input_data_frame

def process_main_tracker(input_file):
    #---------------------------------------------------------------
    # Load the CSV
    data_frame = pd.read_csv(input_file)
    #Uncomment to view data frame
    #print(data_frame)
    #---------------------------------------------------------------
    # Extract all columns starting from the 6th column (Where events start)
    event_data = []
    event_names = data_frame.columns[10:].str.strip().tolist()
    event_class = data_frame.iloc[0, 10:].str.strip().tolist()
    event_dates = data_frame.iloc[1, 10:].str.strip().tolist()
    for index in range(len(event_names)):
        event_attendance = data_frame.iloc[2:, (index + 10)].str.strip().tolist()
        event_data.append(Event(event_names[index], event_class[index], event_dates[index], event_attendance))
    #print(event_data[1].attendance)
    #---------------------------------------------------------------
    # Extracts data starting from the 2nd row (Where students start)
    student_data = []
    student_first_name = data_frame.iloc[2:, 0].str.strip().tolist()
    student_last_name = data_frame.iloc[2:, 1].str.strip().tolist()
    student_class = data_frame.iloc[2:, 2].str.strip().tolist()
    student_family = data_frame.iloc[2:, 3].str.strip().tolist()
    #---------------------------------------------------------------
    # Adds the events (Events attended by students from pre-existing csv)
    for index in range(len(student_first_name)):
        student_event_list = []
        student_row_number = index

        student_attendance = data_frame.iloc[(index + 2), 10:].str.strip().tolist()
        for event_index in range(len(student_attendance)):
            if student_attendance[event_index] != "0":
                student_event_list.append(event_names[event_index])
        #print(student_event_list)
        student_data.append(Student(student_first_name[index], student_last_name[index], student_class[index], student_family[index], student_event_list, student_row_number))
    #---------------------------------------------------------------
    # Returns the event data and student data
    return event_data, student_data

def add_names(student_data, event_data, new_first, new_last):
    def spacer():
        print("\n")

    def pageclear():
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    spacer()
    #---------------------------------------------------------------
    # Input Event Information
    event_name = input("What is the name of the event you are adding? ")
    spacer()
    event_time = input("How long was the event? (In Hours | 1, 1.5, 2): ")
    spacer()
    event_date = input("What is the date of the event? (01/02/2024) ~ Include backslashes) ")

    print("------------------------------------------------------------")
    print("What is the event?")
    print("General Meeting (Q)")
    print("Officer Meeting (W)")
    print("Tabling (E)")
    print("Volunteer (R)")
    print("Social (Y)")
    print("Retreat (U)")
    print("------------------------------------------------------------")
    choice = input()

    if choice.lower() == "q":
        event_type = "General Meeting"
    elif choice.lower() == "w":
        event_type = "Officer Meeting"
    elif choice.lower() == "e":
        event_type = "Tabling"
    elif choice.lower() == "r":
        event_type = "Volunteer"
    elif choice.lower() == "y":
        event_type = "Social"
    elif choice.lower() == "u":
        event_type = "Retreat"
    else:
        print("That is not a choice, please try again")
        main()
    pageclear()


    spacer()
    print(f'The event name is "{event_name}"')
    print(f'The event type is a "{event_type}" event')
    print(f'The event date is {event_date}')
    print(f'The event length is "{event_time} hours')
    confirm = input(f'Y ~ confirm | N ~ to return | E ~ to return to start: ')
    spacer()
    #---------------------------------------------------------------
    # Return to dashboard
    if confirm.lower() == "e":
        main()
    #---------------------------------------------------------------
    # Re-enter event name
    if confirm.lower() == "n":
        print("Please re-enter the event name")
        add_names(student_data, new_first, new_last)
    #---------------------------------------------------------------
    elif confirm.lower() == "y":
        # Ensure new_first and new_last have the same length
        pairs_input = list(zip(new_first, new_last))
        if len(pairs_input) != len(set(pairs_input)):
            print("\n" + "="*60)
            print("ERROR: Duplicate names detected in the attendee list!")
            print("Check names.csv for duplicate entries and try again.")
            print("="*60 + "\n")
            return
        if len(new_first) != len(new_last):
            print("Error: First and last name lists must be of the same length.")
            return

        # Create a set of (first_name, last_name) tuples for faster lookup
        new_students = set(zip(new_first, new_last))

        # Iterate through student_data to find matches
        matched_students = set()  # Track matched (first_name, last_name) pairs
        for student in student_data:
            student_name = (student.first_name, student.last_name)
            if student_name in new_students:
                # Add the event to the student's event list
                student.event_list = event_name
                matched_students.add(student_name)

        # Remove matched students from new_first and new_last
        pairs = list(zip(new_first, new_last))
        for match in matched_students:
            if match in pairs:
                pairs.remove(match)
        new_first = [p[0] for p in pairs]
        new_last  = [p[1] for p in pairs]
        #---------------------------------------------------------------
        # Confirm Addition of New names & Event

        print("Your going to add these new names to the list")
        for index in range(len(new_first)):
            print(f"{new_first[index]} {new_last[index]}")
        
        spacer()
        confirm = input("Enter Y to confirm or N to Exit: ")
        if confirm.lower() == "y":
            #---------------------------------------------------------------
            # Add zeros to previous events for new members and make sure to make event names unique
            original_name = event_name
            blanks = []
            for _ in range(len(new_first)):
                blanks.append(0)

            unique = 0
            for event in event_data:
                event.attendance.extend(blanks)
                if event.name == event_name:
                    unique += 1
                    print(unique)
                    event_name = (original_name + "." + str(unique))
                    


            #---------------------------------------------------------------
            # Addition of New names & Event  
            number = len(student_data) - 1

            for index in range(len(new_first)):
                number += 1
                student_data.append(Student(new_first[index], new_last[index], "Member", "NoFam", [event_name], number))

            event_attendance = []

            for student in student_data:
                if event_name in student.event_list:
                    event_attendance.append(event_time)
                else:
                    event_attendance.append("0")
            
            event_data.append(Event(event_name, event_type, event_date, event_attendance))

            return student_data, event_data


            
        #---------------------------------------------------------------
        # Restart, nothing saved
        if confirm.lower() == "n":
            print("Returning to the main menu")
            main()
        #---------------------------------------------------------------

def apply_event(student_data, event_data, event_name, event_type, event_date, event_time, new_first, new_last):
    """
    Pure (no input() calls) version of the add-event logic for use by the web UI.
    Matches existing students, adds new ones, appends the event, and returns updated lists.
    Returns (student_data, event_data) or raises ValueError on duplicate names.
    """
    pairs_input = list(zip(new_first, new_last))
    if len(pairs_input) != len(set(pairs_input)):
        raise ValueError("Duplicate names detected in attendee list.")

    new_students_set = set(zip(new_first, new_last))
    matched_students = set()
    for student in student_data:
        student_name = (student.first_name, student.last_name)
        if student_name in new_students_set:
            student.event_list = event_name
            matched_students.add(student_name)

    pairs = list(zip(new_first, new_last))
    for match in matched_students:
        if match in pairs:
            pairs.remove(match)
    new_first = [p[0] for p in pairs]
    new_last  = [p[1] for p in pairs]

    # Extend attendance for existing events with zeros for new members
    original_name = event_name
    blanks = [0] * len(new_first)
    unique = 0
    for event in event_data:
        event.attendance.extend(blanks)
        if event.name == event_name:
            unique += 1
            event_name = original_name + "." + str(unique)

    number = len(student_data) - 1
    for index in range(len(new_first)):
        number += 1
        student_data.append(Student(new_first[index], new_last[index], "Member", "NoFam", [event_name], number))

    event_attendance = []
    for student in student_data:
        if event_name in student.event_list:
            event_attendance.append(event_time)
        else:
            event_attendance.append("0")

    event_data.append(Event(event_name, event_type, event_date, event_attendance))
    return student_data, event_data


def classification_getter():
    #---------------------------------------------------------------
    # Member Classification Dashboard
    def pageclear():
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    switch = True
    classification_list = []
    while switch == True:
        print("------------------------------------------------------------")
        print("Who do you want to check the hours for?")
        print("Officer (Q)")
        print("Junior Officer (W)")
        print("Big Sib (E)")
        print("Member (R)")
        print("All (A)")
        print("Done (S)")
        print("------------------------------------------------------------")
        if classification_list:
            print("Current Selection: ", end ="")
            for classification in classification_list:
                print(f"{classification}", end =" ")
            print()
        choice = input()

        #---------------------------------------------------------------
        if choice.lower() == "q":
            classification_list.append("Officer")
        elif choice.lower() == "w":
            classification_list.append("Junior Officer")
        elif choice.lower() == "e":
            classification_list.append("Big Sib")
        elif choice.lower() == "r":
            classification_list.append("Member")
        elif choice.lower() == "a":
            classification_list = ["Officer", "Junior Officer", "Big Sib", "Member"]
            switch = False
        elif choice.lower() == "s":
            switch = False
        else:
            print("This is not an option, please try again ")
        
        pageclear()
    #---------------------------------------------------------------
    # Family Classification Dashboard
    switch = True
    family_list = []
    while switch == True:
        print("------------------------------------------------------------")
        print("Which family do you want to check the hours for?")
        print("Kuromi Family (Q)")
        print("PomPom Family (W)")
        print("Melody Family (E)")
        print("No Family (T)")
        print("All (A)")
        print("Done (S)")
        print("------------------------------------------------------------")
        if classification_list:
            print("Current Selection: ", end ="")
            for family in family_list:
                print(f"{family}", end =" ")
            print()
        choice = input()

        #---------------------------------------------------------------
        if choice.lower() == "q":
            family_list.append("Kuromi")
        elif choice.lower() == "w":
            family_list.append("PomPom")
        elif choice.lower() == "e":
            family_list.append("Melody")
        elif choice.lower() == "t":
            family_list.append("NoFam")
        elif choice.lower() == "a":
            family_list = ["Kuromi", "PomPom", "Melody", "NoFam"]
            switch = False
        elif choice.lower() == "s":
            switch = False
        else:
            print("This is not an option, please try again ")

        pageclear()
    #---------------------------------------------------------------
    # Event Classification Dashboard
    switch = True
    event_list = []
    while switch == True:
        print("------------------------------------------------------------")
        print("What do you want to check the hours for?")
        print("General Meeting (Q)")
        print("Officer Meeting (W)")
        print("Tabling (E)")
        print("Volunteer (R)")
        print("Social (Y)")
        print("Retreat (U)")
        print("All (A)")
        print("Done (S)")
        print("------------------------------------------------------------")
        if event_list:
            print("Current Selection: ", end ="")
            for event in event_list:
                print(f"{event}", end =" ")
            print()
        choice = input()

        #---------------------------------------------------------------
        if choice.lower() == "q":
            event_list.append("General Meeting")
        elif choice.lower() == "w":
            event_list.append("Officer Meeting")
        elif choice.lower() == "e":
            event_list.append("Tabling")
        elif choice.lower() == "r":
            event_list.append("Volunteer")
        elif choice.lower() == "y":
            event_list.append("Social")
        elif choice.lower() == "u":
            event_list.append("Retreat")
        elif choice.lower() == "a":
            event_list = ["General Meeting", "Officer Meeting", "Tabling", "Volunteer", "Social", "Retreat"]
            switch = False
        elif choice.lower() == "s":
            switch = False
        else:
            print("This is not an option, please try again ")

    return(classification_list, family_list, event_list)

def banquet_qual(student_data, event_data):
    #---------------------------------------------------------------
    # Checks to see if members can attend banquet
    banquet_attendance_valid = []

    #---------------------------------------------------------------
    # Isolate General Meeting and Volunteer Events Only
    event_class_dict = defaultdict()
    for event in event_data:
        if event.classification in ["General Meeting", "Volunteer"] and "." not in event.name:
            event_class_dict[event.name] = event.classification

    #---------------------------------------------------------------
    # Checks how many unique volunteer events and general meeting a member has attended
    for student in student_data:
        volunteer = 0
        general_meeting = 0
        student_event_set = set(student.event_list)
        for event in student_event_set:
            if event in event_class_dict.keys():
                if event_class_dict[event] == "General Meeting":
                    general_meeting += 1
                elif event_class_dict[event] == "Volunteer":
                    volunteer += 1
        
        #---------------------------------------------------------------
        # Adds to the validation list to be added to the main Data frame
        
        if volunteer >= 2 and general_meeting >= 1:
            banquet_attendance_valid.append("Yes")

        else:
            banquet_attendance_valid.append("No")
            
    return banquet_attendance_valid

def hour_counter(member_class, valid_family, event_class, student_data, event_data):
    #---------------------------------------------------------------
    # Valid Members
    
    valid_members = []
    for student in student_data:
        if student.classification in member_class and student.family in valid_family:
            valid_members.append(student)

    #---------------------------------------------------------------
    # Valid Events
    valid_event = defaultdict()
    for event in event_data:
        if event.classification in event_class:
            valid_event[event.name] = event

    #---------------------------------------------------------------
    # Count total hours
    member_time = defaultdict(int)
    for member in valid_members:
        member_time[f"{member.first_name} {member.last_name}"] = 0
        #print(member.event_list)
        for event in member.event_list:
            if event in valid_event.keys():
                #print(valid_event[event].attendance)
                #print(member_time)
                member_time[f"{member.first_name} {member.last_name}"] += float(valid_event[event].attendance[member.row_number])
    
    return member_time

def saver(student_data, event_data, savefile):
    #---------------------------------------------------------------
    # First Column (First Name)
    first_col = ["",""]
    for student in student_data:
        first_col.append(student.first_name)

    # Create the DataFrame with a column name
    new_dataframe = pd.DataFrame({"First Name": first_col})

    #---------------------------------------------------------------
    # Second Column (Last Name)
    second_col = ["",""]
    for student in student_data:
        second_col.append(student.last_name)

    new_dataframe["Last Name"] = second_col

    #---------------------------------------------------------------
    # Third Column (Classification)
    third_col = ["",""]
    for student in student_data:
        third_col.append(student.classification)

    new_dataframe["Class"] = third_col

    #---------------------------------------------------------------
    # Fourth Column (Family)
    fourth_col = ["",""]
    for student in student_data:
        fourth_col.append(student.family)

    new_dataframe["Family"] = fourth_col

    #---------------------------------------------------------------
    # Fifth Column (Total)
    fifth_col = ["",""]
    total_hours = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi", "PomPom", "Melody", "NoFam"], 
        ["General Meeting", "Officer Meeting", "Tabling", "Volunteer", "Social", "Retreat"], 
        student_data, event_data
    )
    fifth_col.extend(total_hours.values())
    print(len(fifth_col))
    new_dataframe["Total Hours"] = fifth_col

    #---------------------------------------------------------------
    # Sixth Column (Volunteer)
    sixth_col = ["",""]
    volunteer_hours = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi", "PomPom", "Melody", "NoFam"],
        ["Volunteer"], 
        student_data, event_data
    )
    sixth_col.extend(volunteer_hours.values())
    new_dataframe["Volunteer Hours"] = sixth_col

    #---------------------------------------------------------------
    # Seventh Column (General Meeting)
    seventh_col = ["",""]
    general_hours = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi", "PomPom", "Melody", "NoFam"],
        ["General Meeting"], 
        student_data, event_data
    )
    seventh_col.extend(general_hours.values())
    new_dataframe["General Meeting"] = seventh_col

    #---------------------------------------------------------------
    # Eighth Column (Tabling)
    eighth_col = ["",""]
    tabling_hours = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi", "PomPom", "Melody", "NoFam"],
        ["Tabling"], 
        student_data, event_data
    )
    eighth_col.extend(tabling_hours.values())
    new_dataframe["Tabling"] = eighth_col

    #---------------------------------------------------------------
    # Ninth Column (Social)
    ninth_col = ["",""]
    social_hours = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi", "PomPom", "Melody", "NoFam"],
        ["Social"], 
        student_data, event_data
    )
    ninth_col.extend(social_hours.values())
    new_dataframe["Social"] = ninth_col

    #---------------------------------------------------------------
    # Tenth Column (Banquet Validation)
    tenth_col = ["",""]
    banquet_valid = banquet_qual(student_data, event_data)
    tenth_col.extend(banquet_valid)
    new_dataframe["Banquet"] = tenth_col

    #---------------------------------------------------------------
    # All Events
    for event in event_data:
        event_col = [event.classification, event.date]
        event_col.extend(event.attendance)
        new_dataframe[event.name] = event_col

    new_dataframe.to_csv(savefile, index=False)   

def family_leaderboard(student_data, event_data):

    #---------------------------------------------------------------
    # Event Classification Dashboard
    switch = True
    event_list = []
    while switch == True:
        print("------------------------------------------------------------")
        print("What do you want to check the hours for?")
        print("General Meeting (Q)")
        print("Volunteer (W)")
        print("Social (E)")
        print("All (A)")
        print("Done (S)")
        print("------------------------------------------------------------")
        if event_list:
            print("Current Selection: ", end ="")
            for event in event_list:
                print(f"{event}", end =" ")
            print()
        choice = input()

        #---------------------------------------------------------------
        if choice.lower() == "q":
            event_list.append("General Meeting")
        elif choice.lower() == "w":
            event_list.append("Volunteer")
        elif choice.lower() == "e":
            event_list.append("Social")
        elif choice.lower() == "a":
            event_list = ["General Meeting", "Volunteer", "Social"]
            switch = False
        elif choice.lower() == "s":
            switch = False
        else:
            print("This is not an option, please try again ")
    
    
    families = defaultdict()

    kuromi_family = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Kuromi"], event_list, student_data, event_data)
    families["Kuromi Family"] = sum(kuromi_family.values())

    pompom_family = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["PomPom"], event_list, student_data, event_data)
    families["PomPom Family"] = sum(pompom_family.values())

    melody_family = hour_counter(
        ["Officer", "Junior Officer", "Big Sib", "Member"], ["Melody"], event_list, student_data, event_data)
    families["Melody Family"] = sum(melody_family.values())

    return families

def main():
    def spacer():
        print("\n")
    
    def pageclear():
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    
    #---------------------------------------------------------------
    # Import the new names dataframe
    new_names_df = import_names("names.csv")
    new_first_names = new_names_df.iloc[0:, 0].str.strip().tolist()
    new_last_names = new_names_df.iloc[0:, 1].str.strip().tolist()
    print(len(new_first_names))
    print(len(new_last_names))
    #---------------------------------------------------------------
    # Import the event and student data from the pre-existing data tracker
    event_data, student_data = process_main_tracker('2025_2026_Main_Tracker.csv')
    #---------------------------------------------------------------
    # Create Dashboard
    spacer()
    print("------------------------------------------------------------")
    print("Welcome to the Tzu Chi Hour Tracker")
    print("View data table (Q)")
    print("To add an event (W)")
    print("Hour Counter (E)")
    print("Family Leader Board (R)")
    print("Exit Program (S)")
    print("------------------------------------------------------------")


    decision = input()
    
    if decision.lower() == "q":
        spacer()
        print(pd.read_csv('2025_2026_Main_Tracker.csv'))
        spacer()
        print("Press Enter When Done Viewing")
        input()
        pageclear()
        main()


    if decision.lower() == "w":
        student_data, event_data = add_names(student_data, event_data, new_first_names, new_last_names)
        saver(student_data, event_data, '2025_2026_Main_Tracker.csv')
        pageclear()
        print("Save Occured")
        main()
    
    if decision.lower() == "e":
        pageclear()
        classification_list, family_list, event_list = classification_getter()
        pageclear()
        print(classification_list)
        print(family_list)
        print(event_list)
        spacer()
        choice = input('These are your parameters: Press Enter to continue | Enter "E" to return to main: ')
        if choice.lower() == "e":
            main()
        pageclear()

        member_times = hour_counter(classification_list, family_list, event_list, student_data, event_data)
        try:
            print('Show the top "X" members (Input Positive Integer) ')
            number = int(input())

            if number > len(member_times):
                number = len(member_times)
        except:
            print("That is not a number\nReturning to main")
            spacer()
            spacer()
            main()
        sorted_member_times = dict(sorted(member_times.items(), key=lambda item: item[1], reverse=True))
        member_times_list = list(sorted_member_times.items())
        for index in range(number):
            print(f"{member_times_list[index][0]}: {member_times_list[index][1]}")
            

    if decision.lower() == "r":
        pageclear()
        family_dict = family_leaderboard(student_data, event_data)
        sorted_family_times = dict(sorted(family_dict.items(), key=lambda item: item[1], reverse=True))
        family_list = list(sorted_family_times.items())
        pageclear()
        for index in range(len(family_list)):
            print(f"{family_list[index][0]}: {family_list[index][1]}")
        spacer()
        print("Press Enter When Done Viewing")
        input()
        pageclear()
        main()
    
    if decision.lower() == "s":
        saver(student_data, event_data, '2025_2026_Main_Tracker.csv')
        pageclear()
        print("Have a good day!")


if __name__ == '__main__':
    main()
