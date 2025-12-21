# How to Download Wiki Page Sources

To manually fetch the edit source for each realm page, follow these steps:

## Option 1: Manual Download (Easiest)
For each realm, visit the edit source URL and copy the content:


### Main Realm
1. Open: https://ftbc.fandom.com/wiki/Main_Realm?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Main_Realm.txt
4. Paste the content

### Yoyle Factory
1. Open: https://ftbc.fandom.com/wiki/Yoyle_Factory?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Yoyle_Factory.txt
4. Paste the content

### Backrooms
1. Open: https://ftbc.fandom.com/wiki/Backrooms?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Backrooms.txt
4. Paste the content

### Inverted Realm
1. Open: https://ftbc.fandom.com/wiki/Inverted_Realm?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Inverted_Realm.txt
4. Paste the content

### Yoyleland
1. Open: https://ftbc.fandom.com/wiki/Yoyleland?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Yoyleland.txt
4. Paste the content

### Classic Paradise
1. Open: https://ftbc.fandom.com/wiki/Classic_Paradise?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Classic_Paradise.txt
4. Paste the content

### Evil Forest
1. Open: https://ftbc.fandom.com/wiki/Evil_Forest?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Evil_Forest.txt
4. Paste the content

### Cherry Grove
1. Open: https://ftbc.fandom.com/wiki/Cherry_Grove?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Cherry_Grove.txt
4. Paste the content

### Barren Desert
1. Open: https://ftbc.fandom.com/wiki/Barren_Desert?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Barren_Desert.txt
4. Paste the content

### Frozen World
1. Open: https://ftbc.fandom.com/wiki/Frozen_World?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Frozen_World.txt
4. Paste the content

### Timber Peaks
1. Open: https://ftbc.fandom.com/wiki/Timber_Peaks?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Timber_Peaks.txt
4. Paste the content

### Midnight Rooftops
1. Open: https://ftbc.fandom.com/wiki/Midnight_Rooftops?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Midnight_Rooftops.txt
4. Paste the content

### Magma Canyon
1. Open: https://ftbc.fandom.com/wiki/Magma_Canyon?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Magma_Canyon.txt
4. Paste the content

### Sakura Serenity
1. Open: https://ftbc.fandom.com/wiki/Sakura_Serenity?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Sakura_Serenity.txt
4. Paste the content

### Polluted Marshlands
1. Open: https://ftbc.fandom.com/wiki/Polluted_Marshlands?veaction=editsource
2. Select all (Ctrl+A) and copy
3. Create file: pages/Polluted_Marshlands.txt
4. Paste the content


## Option 2: Browser Script (Automated)
Paste this in browser DevTools console (will prompt for each page):

```javascript
const realms = [
    'Main Realm', 'Yoyle Factory', 'Backrooms', 'Inverted Realm',
    'Yoyleland', 'Classic Paradise', 'Evil Forest', 'Cherry Grove',
    'Barren Desert', 'Frozen World', 'Timber Peaks', 'Midnight Rooftops',
    'Magma Canyon', 'Sakura Serenity', 'Polluted Marshlands'
];

for (const realm of realms) {
    const url = `https://ftbc.fandom.com/wiki/${realm.replace(/ /g, '_')}?veaction=editsource`;
    console.log(`Open: ${url}`);
}
```

## Option 3: Bulk Copy via Edit History
1. Go to each realm page
2. Click "Edit source" button
3. Copy all text
4. Save to pages/[Realm Name].txt

---

Once downloaded, files will be in the `/pages/` directory for local reference.
