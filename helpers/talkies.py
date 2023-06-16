import random

excited_lines = [
    "I want to become everybody! Who says I cannot? I will prove them wrong! Then, I will become them. Last laugh? Neeko!",
    "Neeko keeps a tiny bit of everybody's sho'ma. They are precious!",
    "After fight ends, everyone invited to picnic! Even enemies.",
    "Neeko strong! Can take on world!",
    "Slow down? No! Fast fast fast!",
    "What to do now? Find cheesebreads? Ooh! Have picnic!",
    "Who stands in Neeko's way? Dummies with small sho'ma, that's who!",
    "What does Neeko do with power? Make people behave.",
    "Stand back! Big strong Neeko coming though!",
    "This is very exciting! Everything is falling down!",
    "Everyone fears Neeko now! Hahaha!",
    "Beauty shines from inside, where the heart dances.",
    "Ahhh!! Neeko on fire! Just kidding."
]

not_so_excited_lines = [
    "Neeko does not want to be here when... the others arrive.",
    "I will learn! I will grow! I will... Neeko!",
    "Be cool. No one suspects you are Neeko.",
    "*(Neeko whistles)* I am definitely not Neeko. Nope. Not Neeko.",
    "*Neeko laughs awkwardly.*",
    "Yuck! Take a bath. Gross."
]

def get_excited_line():
    return random.choice(excited_lines)

def get_sad_line():
    return random.choice(not_so_excited_lines)