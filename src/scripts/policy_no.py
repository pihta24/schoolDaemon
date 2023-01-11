import xml.etree.ElementTree as ET
tree = ET.parse('/usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy')
root = tree.getroot()
for child in root[13][74]:
    child.text = 'no'
for child in root[14][74]:
    child.text = 'no'
tree.write('/usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy')