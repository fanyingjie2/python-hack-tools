

f=open("ip.txt",'a')
for i in range(1,2):
	for a in range(1,2):
		for b in range(1,255):
			for c in range(1,255):
				line="111.13."+str(b)+"."+str(c)
				f.write(line+"\n")
f.close()
