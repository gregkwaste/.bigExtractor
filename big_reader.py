#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      gregkwaste
#
# Created:     21/09/2014
# Copyright:   (c) gregkwaste 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import struct,os

def read_string(f):
	c=''
	for i in range(128):
		s=struct.unpack('<B',f.read(1))[0]
		if s==0:
			return c
		c=c+chr(s)

	return {'FINISHED'}


#f=open('C:\\Users\\gregkwaste\\Downloads\\4557441-FFFFFFF15SG\\FIFA 15\\data_ini_extra.big')
f=open('C:\\Users\\gregkwaste\\Downloads\\4557441-FFFFFFF15SG\\FIFA 15\\data_graphic2_extra.big','rb')
header=f.read(4)
full_size=struct.unpack('>I',f.read(4))[0]
file_count=struct.unpack('>I',f.read(4))[0]
def_size=struct.unpack('>I',f.read(4))[0]

t=open('C:\\'+f.name.split('\\')[-1].split('.')[0]+'.index','w')


file_list=[]
for i in range(file_count):
    data_off=struct.unpack('>I',f.read(4))[0]
    data_size=struct.unpack('>I',f.read(4))[0]
    data_name=read_string(f)
    file_list.append((data_off,data_size,data_name))
    t.write(str(i)+' '+data_name+'\n')

t.close()

f=open('C:\\Users\\gregkwaste\\Downloads\\4557441-FFFFFFF15SG\\FIFA 15\\data_graphic2_extra.big','rb')


for i in range(15078,len(file_list)):
    f.seek(file_list[i][0]) #go to archive offset
    #prepare directories
    data_path=file_list[i][2].split('/')
    t_path=''
    for name in data_path:
        t_path+='\\'+name

    t_path='C:\\'+f.name.split('\\')[-1].split('.')[0]+t_path
    if not os.path.exists(os.path.dirname(t_path)):
        os.makedirs(os.path.dirname(t_path))

    t=open(t_path,'wb')
    t.write(f.read(file_list[i][1]))
    t.close()


f.close()