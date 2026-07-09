import random
subjects=[
    "Sharukh Khan",
    "Virat Kohaki",
    "Nirmala Sitaraman",
    "A mumbai Cat",
    "A groups of monkey ",
    "Prime Minister Modi",
    "Auto Rikhaw Driver From new  Delhi"
]

actions  =[
    "lunches",
    "cancels",
    "eats",
    "declares war on ",
    "order AK47 ",#####
    "celebraties"
]
place_or_things=[
    "At red fort",
    "in mumbai Local train"
    "a plot of samaosa",
    "at ganga ghat",
    "during IPL Match",
    "At India Gate"
]
while True :
    subject= random.choice(subjects)
    action=random.choice(actions)
    place_or_thing=random.choice(place_or_things)
    headline = f"Breaking News:{subject} {action} {place_or_thing}"
    print("\n"+headline)
    user_input = input("\nDo you want another Headlines?  (YES/NO)").strip().upper()
    if user_input=="No" and no  and NO :
        break
    print("\nThanks for using the fake news Headlines Genrator .Have a Fun")


