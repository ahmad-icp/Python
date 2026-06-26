#strings and functions on strings
names = "Ahmad,Ali,Anas,Asad"
print(names)
#For paragraph writing or string with two lines we use 
paragraph="""The Windows installers and all binaries produced
 as part of each Python release are signed using an Authenticode signing 
 certificate issued to the Python Software Foundation. This can be verified by
 viewing the properties of any executable file,
 looking at the Digital Signatures tab, and confirming the name of the signer"""
print(paragraph)
      
#length of string
print("There are",len(paragraph),"words in this paragraph")

#string indexing and slicing
print(paragraph[0])  #first character
print(paragraph[1:15])  #for multiple characters
print(paragraph[0:100:2])  #for every second character
print(paragraph[-1])  #last character
print(paragraph[-12:-1])  #for multiple last characters

#converting sting to uppercase and lowercase
print(names.upper())
print(names.lower())

#replacing a word in string
print(paragraph.replace("Python","Java"))