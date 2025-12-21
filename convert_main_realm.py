#!/usr/bin/env python3
"""Convert Main_Realm.txt remaining sections to ObjectDifficultyList format"""

# Define all difficulty sections with their data
difficulties_data = [
    {
        'name': 'Normal',
        'color': '#a1ff27',
        'icon': 'Normal.png',
        'objects': [
            '8-Ball', '9-Ball', 'Amethysty', 'Awesome Face', 'Baking Soda', 'Ball',
            'Balloony', 'Bally', 'BFDI Marker', 'Bitty', 'Blender', 'Bottle',
            'Bracelety', 'Butter', 'Buzzsaw', 'Car Engine', 'Cave Drawing', 'Cheese',
            'Chestnut', 'Chocolate Bar', 'Clover', 'Cologne', 'Cookie Pizza', 'Dark Gemstone',
            'Domino', 'Drinky Bird', 'Fettuccine', 'Firey Jr.', 'Fourteen', 'Green Egg',
            'Hexagon', 'Kabab', 'Lemonade', 'Lightning', 'Lollipop', 'Meat Cube',
            'Metal Scrap', 'Milkshake', 'Nine and Six Combined', 'Pasty', 'Plump Dog', 'Pop Tart',
            'Purple Dragon', 'Robot Flower', 'Rocky', 'Ruby', 'Seaweed', 'Slug',
            'S\'mores Milkshake', 'Snake', 'Taco Guy', 'Triangle', 'USB', 'V'
        ]
    },
    {
        'name': 'Intermediate',
        'color': '#ffb700',
        'icon': 'Intermediate FTBC.png',
        'objects': [
            'Banana', 'Bird', 'Blanket', 'Blue Lion', 'Blue Shiny Coiny', 'Boom Mic',
            'Bready', 'Cartridge', 'Chanterelle', 'Chef David', 'Crate', 'David',
            'Davidworm', 'Dollar Bill', 'Flower Crown', 'Fortune Cookie', 'Four and X', 'Genderfluid Book',
            'Good Rhombicodidodecahedron', 'Green Rocky', 'Idoit', 'Knifeball', 'Lever', 'Lip Gloss',
            'Mail', 'Meteor', 'Miku', 'Milli Book', 'Pea', 'Pixelated Heart',
            'Remote', 'Sand Jar', 'SD Card', 'Seven', 'Six', 'Spoony',
            'Succulent', 'Symbol', 'Tabley', 'Texas Donut', 'Well'
        ]
    },
    {
        'name': 'Hard',
        'color': '#ff7e21',
        'icon': 'Hard.png',
        'objects': [
            'Air', 'Among Us X', 'Barf Molecule', 'Blob', 'Bowling Ball', 'Bright Radiant Plasma Needle',
            'Calculator', 'Candy', 'Candy Corn', 'Cary', 'Cat', 'Chocolate Chip',
            'Chocolate Pop', 'Coffee Bean', 'Diskette', 'Eggy', 'English Cream Cake', 'Fire Spatula',
            'Fossil', 'Fridge', 'Fronk', 'Gear', 'Giant Tree', 'Gifty',
            'Halporhini Cube', 'Ice Cube', 'Irony', 'Jawbreaker', 'Liy', 'Mardi Gras Bead',
            'Marimo Ball', 'Mechanical Pencil', 'Minty', 'Nine', 'Palmy', 'Peanut Butter',
            'Pebble', 'Purple Face', 'Rollarskate', 'Slide Man', 'Spark Plug', 'Sundae',
            'Tablety', 'Titanium Knife', 'Tri-Tri', 'Tungsten', 'Two Halves', 'Vomit Drop',
            'Yellow Face'
        ]
    },
    {
        'name': 'Difficult',
        'color': '#f54f25',
        'icon': 'Difficult.png',
        'objects': [
            'Battery', 'Black Marker', 'Bluecky', 'Blue Needle', 'Blue Square', 'Boaty',
            'Box Fan', 'Clapboard', 'De Stijl', 'Dora', 'Em', 'Fire',
            'Fish Bowl', 'Four', 'Function', 'Hailairhous', 'Headphones', 'Image',
            'Jingle Bell', 'Junior', 'Lasagna', 'Lily', 'Long Marker', 'Metal Leafy',
            'One Way Sign', 'Orange Cat', 'Paper', 'Pastel Feather', 'PDA', 'Portable Music Player',
            'Puffball', 'Santa Hat', 'Shampoo', 'Snowball', 'Swiss Roll', 'Tennis Ball',
            'Tennis Ball Speaker Box', 'The First Frame', 'Touch-Tone', 'Tropical Virtual Pet Lizard', 'Wet Clay', 'Win Token',
            'World Map', 'Yellow Watermelon', 'Yoyle Pie', 'YSA Status'
        ]
    },
    {
        'name': 'Extreme',
        'color': '#ED2727',
        'icon': 'Extreme.png',
        'objects': [
            'Air Freshener', 'Beach Ball', 'Bead', 'Bomby Plush', 'Cake Pop', 'Comet',
            'Controller', 'CRT', 'Dog Collar', 'Earth', 'Evil Bubble', 'Falafel',
            'Gashapon Capsule', 'Green Square', 'Homeless Spooky', 'Income Tax Return Document', 'Irregular Polygon', 'Lava Ball',
            'Lego Brick', 'Microwave', 'Mocha', 'Omega', 'Pie', 'Pixely',
            'Poker Chip', 'Puffball Speaker Box', 'Raising Cane\'s Cup', 'Red Mushroom', 'Revolver', 'Shoiyta',
            'Steamboat Hat', 'Strudel', 'Taco With Tophat', 'Tune', 'Uni', 'Vanilla Milkshake',
            'Weird Speaker Box'
        ]
    },
    {
        'name': 'Unforgiving',
        'color': '#ff143f',
        'icon': 'Unforgiving.png',
        'objects': [
            'Beanbag', 'Cake', 'Credit Card', 'Demonic Painting', 'Drilly', 'Earphone Shotgun',
            'Exploding David', 'Feet', 'Firey Speaker Box', 'Gumbally', 'Lampy', 'Leafy Jr.',
            'Monarch', 'Onigiri', 'Ordinary Banana...', 'Peanut', 'Quartz', 'Roboty-y',
            'Spike Ball', 'Stool', 'Sun', 'Thirteen', 'Tombstone', 'Yellow Leopard',
            'Zombified Barf Bag'
        ]
    },
    {
        'name': 'Insane',
        'color': '#FF1C95',
        'icon': 'Insane.png',
        'objects': [
            'Black Hole', 'Bubble', 'Buh', 'Feather', 'Flower Speaker Box', 'Four Colored Gelatin',
            'Frozen Yogurt', 'Geode', 'Gingerbread Man', 'Laser Pointer', 'Pride Cat Firey', 'Shinyleaf',
            'Sippy', 'THE GET AWAY FROM ME BUTTON!!!!!!!', 'Trash Can', 'Two', 'X'
        ]
    },
    {
        'name': 'Dreadful',
        'color': '#db25ff',
        'icon': 'Dreadful.png',
        'objects': [
            'Bandana', 'd', 'Immortality Thing', 'Jellybean Jar', 'Sad Cloudy', 'Safe',
            'Torch', 'Troll Face'
        ]
    },
    {
        'name': 'Terrifying',
        'color': '#8b17ff',
        'icon': 'Terrifying.png',
        'objects': [
            'Chicken Nuggets', 'Evidence Bag', 'Replicated Storage', 'Quereltrajankyn', 'Sharp', 'Slime Flashlight',
            'This is Sparta-Y'
        ]
    },
    {
        'name': 'Arduous',
        'color': '#5d0cff',
        'icon': 'Arduous.png',
        'objects': [
            'Alien', 'Boblob', 'Burger', 'Filler', 'Nanoboty', 'Nonexisty',
            'Studio', 'Throne', 'Tiddles', 'Ulm'
        ]
    },
    {
        'name': 'Strenuous',
        'color': '#4048E5',
        'icon': 'Strenuous.png',
        'objects': [
            'Brainy', 'Cauldron', 'Every Character Fused', 'Fedora', 'Glitchy', 'Hornbox',
            'King Skull', 'Poison Cake', 'Transmitter'
        ]
    },
    {
        'name': 'Remorseless',
        'color': '#2084FF',
        'icon': 'Remorseless.png',
        'objects': [
            'ARG Television', 'Chartreuse', 'Front Facing Marker', 'Remote Event', 'SilvaGunner', 'Storm Ball'
        ]
    },
    {
        'name': 'Horrifying',
        'color': '#2bd0fd; -webkit-text-stroke-width: 1px; -webkit-text-stroke-color: #72e1ff',
        'icon': 'Horrifying.png',
        'objects': [
            'Starwalker', 'Wand'
        ]
    },
]

def create_template(data):
    """Create ObjectDifficultyList template for a difficulty"""
    gallery_lines = []
    for obj in data['objects']:
        gallery_lines.append(f'File:{obj}.png|[[File:{data["icon"]}|18px]] \'\'\' [[{obj}]] \'\'\'')
    
    gallery = '\n'.join(gallery_lines)
    
    template = f"""{{{{ObjectDifficultyList
|name = {data['name']}
|icon = {data['icon']}
|color = {data['color']}
|total = {len(data['objects'])}
|gallery =
<gallery widths="60" heights="60" mode="packed">
{gallery}
</gallery>
}}}}"""
    return template

# Read file
with open('pages/realms/Main_Realm.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace REPLACED_NORMAL_HERE marker with Normal template
normal_data = difficulties_data[0]
normal_template = create_template(normal_data)
content = content.replace('REPLACED_NORMAL_HERE', f'------------------------------------------------------------\n\n{normal_template}\n')

# Write back
with open('pages/realms/Main_Realm.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Conversion complete!")
print("Next: Replace remaining difficulty sections manually or with subsequent script runs")
